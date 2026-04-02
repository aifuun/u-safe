# Pillar P: Circuit Breaking & Safe Mode

> Detect failures and degrade gracefully

## Rule

System must detect downstream failures and automatically degrade to **Safe Mode** when error thresholds are exceeded.

## Purpose

- Fail fast when downstream is unhealthy
- Prevent cascade failures
- Provide degraded but usable experience
- Allow time for recovery

## Implementation

### Circuit Breaker States

```typescript
type CircuitState = 'closed' | 'open' | 'half-open';

interface CircuitBreaker {
  state: CircuitState;
  failureCount: number;
  lastFailureTime: Date | null;
  successCount: number;  // For half-open
}

interface CircuitConfig {
  failureThreshold: number;    // Failures to open
  successThreshold: number;    // Successes to close
  timeout: number;             // ms before half-open
  monitorWindow: number;       // ms for failure counting
}
```

### Circuit Breaker Implementation

```typescript
// infrastructure/circuitBreaker.ts

class CircuitBreaker {
  private state: CircuitState = 'closed';
  private failures: Date[] = [];
  private halfOpenSuccesses = 0;

  constructor(
    private name: string,
    private config: CircuitConfig
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // Check if circuit is open
    if (this.state === 'open') {
      if (this.shouldAttemptReset()) {
        this.state = 'half-open';
        this.halfOpenSuccesses = 0;
      } else {
        throw new CircuitOpenError(this.name);
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    if (this.state === 'half-open') {
      this.halfOpenSuccesses++;
      if (this.halfOpenSuccesses >= this.config.successThreshold) {
        this.reset();
        logger.json('CIRCUIT_CLOSED', { name: this.name });
      }
    }
  }

  private onFailure(): void {
    const now = new Date();

    // Clean old failures outside monitoring window
    this.failures = this.failures.filter(
      f => now.getTime() - f.getTime() < this.config.monitorWindow
    );

    this.failures.push(now);

    if (this.failures.length >= this.config.failureThreshold) {
      this.state = 'open';
      logger.json('CIRCUIT_OPENED', {
        name: this.name,
        failures: this.failures.length,
      });
    }
  }

  private shouldAttemptReset(): boolean {
    const lastFailure = this.failures[this.failures.length - 1];
    if (!lastFailure) return true;

    return Date.now() - lastFailure.getTime() > this.config.timeout;
  }

  private reset(): void {
    this.state = 'closed';
    this.failures = [];
    this.halfOpenSuccesses = 0;
  }
}
```

### Service with Circuit Breaker

```typescript
// adapters/paymentAdapter.ts

const paymentCircuit = new CircuitBreaker('payment-service', {
  failureThreshold: 5,
  successThreshold: 3,
  timeout: 30000,
  monitorWindow: 60000,
});

async function chargePayment(amount: Money): Promise<PaymentResult> {
  try {
    return await paymentCircuit.execute(async () => {
      return await stripeClient.charges.create({ amount });
    });
  } catch (error) {
    if (error instanceof CircuitOpenError) {
      // Return safe mode response
      return {
        status: 'degraded',
        message: 'Payment service temporarily unavailable',
        retryAfter: 30,
      };
    }
    throw error;
  }
}
```

### Safe Mode UI

```typescript
// headless/useSafeMode.ts

interface SafeModeState {
  isActive: boolean;
  degradedServices: string[];
  message: string;
}

function useSafeMode(): SafeModeState {
  const [state, setState] = useState<SafeModeState>({
    isActive: false,
    degradedServices: [],
    message: '',
  });

  useEffect(() => {
    const checkHealth = async () => {
      const health = await api.getSystemHealth();

      setState({
        isActive: health.degradedServices.length > 0,
        degradedServices: health.degradedServices,
        message: health.message,
      });
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return state;
}

// View with safe mode awareness
function CheckoutButton() {
  const { isActive: safeMode, message } = useSafeMode();
  const { checkout, isLoading } = useCheckout();

  if (safeMode) {
    return (
      <div className="safe-mode-banner">
        <p>{message}</p>
        <button disabled>Checkout Unavailable</button>
      </div>
    );
  }

  return <button onClick={checkout}>Checkout</button>;
}
```

### Fallback Strategies

```typescript
// Cached fallback
async function getProductCatalog(): Promise<Product[]> {
  try {
    return await catalogCircuit.execute(() => catalogApi.getAll());
  } catch (error) {
    if (error instanceof CircuitOpenError) {
      // Return cached data
      const cached = await cache.get('product-catalog');
      if (cached) {
        return { ...cached, stale: true };
      }
    }
    throw error;
  }
}

// Partial degradation
async function getOrderDetails(orderId: OrderId): Promise<OrderDetails> {
  const order = await orderService.get(orderId);

  // Try to enrich with recommendations
  let recommendations: Product[] = [];
  try {
    recommendations = await recommendationCircuit.execute(
      () => recommendationService.forOrder(orderId)
    );
  } catch {
    // Recommendations unavailable - continue without
  }

  return { ...order, recommendations };
}
```

## Graceful Degradation Patterns

When circuits open, provide degraded but functional service instead of complete failure.

### 1. Cached Fallback

Return stale data when the circuit is open:

```typescript
async function getRecommendations(userId: UserId): Promise<Product[]> {
  // Check circuit state first
  if (recommendationCircuit.isOpen()) {
    logger.warn('CIRCUIT_OPEN_FALLBACK', { service: 'recommendations', userId });
    return getCachedRecommendations(userId);
  }

  try {
    const products = await recommendationCircuit.execute(async () => {
      return await recommendationService.fetch(userId);
    });

    // Cache successful results
    await cacheRecommendations(userId, products);
    return products;
  } catch (error) {
    recommendationCircuit.recordFailure();

    // Fallback to cache
    const cached = await getCachedRecommendations(userId);
    if (cached) {
      return cached.map(p => ({ ...p, stale: true }));
    }

    // Last resort: default recommendations
    return getDefaultRecommendations();
  }
}
```

### 2. Default Fallback

Provide sensible defaults when service is unavailable:

```typescript
async function getUserPreferences(userId: UserId): Promise<UserPreferences> {
  try {
    return await preferencesCircuit.execute(async () => {
      return await preferencesService.get(userId);
    });
  } catch (error) {
    if (error instanceof CircuitOpenError) {
      // Return safe defaults
      return {
        theme: 'light',
        language: 'en',
        notifications: false,
        source: 'default',  // Mark as degraded
      };
    }
    throw error;
  }
}
```

### 3. Progressive Enhancement

Core functionality works even when enhancement services fail:

```typescript
async function getProductPage(productId: ProductId): Promise<ProductPage> {
  // Core product data (critical path)
  const product = await productService.get(productId);

  // Enhancement 1: Reviews (optional)
  let reviews: Review[] = [];
  try {
    reviews = await reviewCircuit.execute(() => reviewService.getForProduct(productId));
  } catch {
    logger.info('REVIEWS_DEGRADED', { productId });
    // Continue without reviews
  }

  // Enhancement 2: Related products (optional)
  let relatedProducts: Product[] = [];
  try {
    relatedProducts = await recommendationCircuit.execute(() =>
      recommendationService.getRelated(productId)
    );
  } catch {
    logger.info('RECOMMENDATIONS_DEGRADED', { productId });
    // Continue without recommendations
  }

  // Enhancement 3: Real-time inventory (optional)
  let inventory: Inventory | null = null;
  try {
    inventory = await inventoryCircuit.execute(() =>
      inventoryService.getStock(productId)
    );
  } catch {
    logger.info('INVENTORY_DEGRADED', { productId });
    // Show product without live inventory count
  }

  return {
    product,
    reviews,
    relatedProducts,
    inventory,
    degradedServices: [
      !reviews.length && 'reviews',
      !relatedProducts.length && 'recommendations',
      !inventory && 'inventory'
    ].filter(Boolean),
  };
}
```

### 4. User Communication

Inform users about degraded operation and recovery:

```typescript
interface ServiceStatus {
  isHealthy: boolean;
  degradedServices: string[];
  estimatedRecoveryTime?: Date;
  userMessage: string;
}

async function getServiceStatus(): Promise<ServiceStatus> {
  const circuits = {
    payment: paymentCircuit,
    shipping: shippingCircuit,
    inventory: inventoryCircuit,
  };

  const degraded = Object.entries(circuits)
    .filter(([_, circuit]) => circuit.isOpen())
    .map(([name]) => name);

  if (degraded.length === 0) {
    return {
      isHealthy: true,
      degradedServices: [],
      userMessage: '',
    };
  }

  // Estimate recovery based on timeout config
  const estimatedRecoveryTime = new Date(
    Date.now() + paymentCircuit.config.timeout
  );

  return {
    isHealthy: false,
    degradedServices: degraded,
    estimatedRecoveryTime,
    userMessage: generateUserMessage(degraded),
  };
}

function generateUserMessage(degradedServices: string[]): string {
  if (degradedServices.includes('payment')) {
    return 'Payment processing is temporarily unavailable. You can browse and add items to your cart. We\'ll notify you when checkout is available.';
  }

  if (degradedServices.includes('inventory')) {
    return 'Real-time inventory information is temporarily unavailable. Orders will be confirmed after placement.';
  }

  return 'Some features are temporarily limited. Core functionality remains available.';
}

// Display in UI
function ServiceStatusBanner() {
  const [status, setStatus] = useState<ServiceStatus>({ isHealthy: true, degradedServices: [], userMessage: '' });

  useEffect(() => {
    const check = async () => {
      setStatus(await getServiceStatus());
    };
    check();
    const interval = setInterval(check, 30000);  // Check every 30s
    return () => clearInterval(interval);
  }, []);

  if (status.isHealthy) return null;

  return (
    <div className="degraded-mode-banner">
      <InfoIcon />
      <p>{status.userMessage}</p>
      {status.estimatedRecoveryTime && (
        <small>Estimated recovery: {formatTime(status.estimatedRecoveryTime)}</small>
      )}
    </div>
  );
}
```

### 5. Graceful Recovery

Automatically resume normal operation when service recovers:

```typescript
class CircuitBreakerWithGracefulRecovery extends CircuitBreaker {
  private onRecoveryCallbacks: Array<() => void> = [];

  onRecovery(callback: () => void): void {
    this.onRecoveryCallbacks.push(callback);
  }

  protected reset(): void {
    super.reset();

    // Notify all subscribers about recovery
    this.onRecoveryCallbacks.forEach(callback => {
      try {
        callback();
      } catch (error) {
        logger.error('RECOVERY_CALLBACK_ERROR', { error });
      }
    });

    logger.json('CIRCUIT_RECOVERED', {
      name: this.name,
      downtime: this.calculateDowntime(),
    });
  }

  private calculateDowntime(): number {
    const firstFailure = this.failures[0];
    if (!firstFailure) return 0;
    return Date.now() - firstFailure.getTime();
  }
}

// Usage
const paymentCircuit = new CircuitBreakerWithGracefulRecovery('payment', config);

paymentCircuit.onRecovery(() => {
  // Clear cached "payment unavailable" messages
  cache.delete('payment-degraded-message');

  // Notify users waiting for checkout
  notificationService.send({
    type: 'service-recovered',
    message: 'Payment processing is now available',
  });

  // Flush queued payment operations
  paymentQueue.resume();
});
```

### When to Use Each Pattern

**Cached Fallback** - Use when:
- Data changes infrequently
- Stale data is acceptable
- Example: Product catalog, user profiles

**Default Fallback** - Use when:
- Safe defaults exist
- Preferences are non-critical
- Example: UI themes, feature flags

**Progressive Enhancement** - Use when:
- Core functionality can work independently
- Enhancements are nice-to-have
- Example: Product pages with optional reviews

**User Communication** - Always use when:
- Degraded mode affects user experience
- Users might retry failed actions
- Recovery time is predictable

## Good Example

```typescript
// ✅ Complete circuit breaker with safe mode

const externalApiCircuit = new CircuitBreaker('external-api', config);

async function fetchExternalData(): Promise<Data> {
  try {
    return await externalApiCircuit.execute(() => externalApi.fetch());
  } catch (error) {
    if (error instanceof CircuitOpenError) {
      logger.warn('SAFE_MODE_ACTIVE', { service: 'external-api' });

      // Try cache
      const cached = await cache.get('external-data');
      if (cached) {
        return { ...cached, source: 'cache', stale: true };
      }

      // Return degraded response
      return {
        data: [],
        source: 'fallback',
        message: 'Service temporarily unavailable',
      };
    }
    throw error;
  }
}
```

## Bad Example

```typescript
// ❌ No circuit breaker - cascade failure
async function fetchData() {
  // Every request hits failing service
  // No timeout, hangs forever
  // Brings down entire system
  return await failingService.fetch();
}

// ❌ Circuit without fallback
async function fetchData() {
  return await circuit.execute(() => service.fetch());
  // CircuitOpenError crashes the app!
}
```

## Anti-Patterns

1. **No timeout on circuit calls**
   ```typescript
   // ❌ Can hang forever
   await circuit.execute(() => slowService.call());
   ```

2. **Circuit without monitoring**
   ```typescript
   // ❌ No visibility into circuit state
   const circuit = new CircuitBreaker(config);
   // No logging, no metrics
   ```

3. **Immediate retry loop**
   ```typescript
   // ❌ Hammers failing service
   while (true) {
     try { return await service.call(); }
     catch { continue; }
   }
   ```

4. **All-or-nothing degradation**
   ```typescript
   // ❌ Should degrade gracefully
   if (anyServiceDown) showErrorPage();
   ```

## Exceptions

- Internal services with guaranteed availability
- Critical path with no fallback possible

## Checklist

- [ ] External services wrapped in circuit breakers
- [ ] Failure thresholds configured appropriately
- [ ] Safe mode UI informs users
- [ ] Cached fallbacks available
- [ ] Circuit state logged for monitoring
- [ ] Write operations disabled in safe mode
- [ ] Fallback strategies defined for each dependency
- [ ] Degraded modes provide partial functionality
- [ ] Users are informed of degraded operation
- [ ] Graceful recovery when dependency returns

## References

- Related: Pillar O (Async) - timeout handling
- Related: Pillar R (Observability) - circuit state logging
- Pattern: Circuit Breaker, Bulkhead, Retry with Backoff

## Assets

- Template: `.claude/pillars/pillar-p/circuit.ts`
- Checklist: `.claude/pillars/pillar-p/checklist.md`

## Changelog

### Version 2.1.0 (2026-03-14)

**Issue**: #195 - Phase 2: Integrate missing best practices

**Changes**:
- ✅ Added comprehensive "Graceful Degradation Patterns" section
- ✅ Covered 5 degradation strategies (Cached Fallback, Default Fallback, Progressive Enhancement, User Communication, Graceful Recovery)
- ✅ Demonstrated degraded mode vs failure mode
- ✅ Added cached fallback patterns with stale data handling
- ✅ Showed progressive enhancement approach for optional features
- ✅ Added user communication examples
- ✅ Added graceful degradation checklist items

**Impact**:
- Graceful Degradation best practice now covered (Resilience category)
- Developers have clear patterns for maintaining functionality during outages
- Combines circuit breaking with intelligent fallback strategies
- Improves user experience during partial system failures

**Backward compatibility**: All existing content preserved, purely additive change
