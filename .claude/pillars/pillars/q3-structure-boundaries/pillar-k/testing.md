# Pillar K: The Testing Pyramid

> Test strategy differs by architectural layer

## Rule

Apply different testing strategies to different layers:
- **Domain**: 100% unit test coverage
- **Adapters**: Contract tests
- **Workflows/Sagas**: Integration tests

## Purpose

- Optimal test coverage per layer
- Fast feedback from unit tests
- Confidence from integration tests
- Avoid slow, brittle E2E tests for logic

## Core Concept

Different architectural layers require different testing strategies. Use the Testing Pyramid: many fast unit tests at the bottom, fewer slow E2E tests at the top.

**Key Principle**: Test business logic with fast unit tests. Reserve integration/E2E tests for workflows and critical user journeys.

## Generic Implementation (Test Framework Agnostic)

### Testing Pyramid

```
                    /\
                   /  \
                  / E2E\         ← Fewest (critical paths only)
                 /──────\
                /        \
               /Integration\     ← Workflows, Sagas
              /────────────\
             /              \
            /   Contract     \   ← Adapters, API boundaries
           /──────────────────\
          /                    \
         /       Unit           \ ← Domain, Logic (most tests)
        /────────────────────────\
```

### Layer 1: Domain/Business Logic (Unit Tests)

Test pure functions with no external dependencies.

```typescript
// Pure business logic - no framework imports
function calculateOrderTotal(
  items: Array<{ price: number; quantity: number }>,
  options?: { discount?: number }
): number {
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  return options?.discount ? subtotal - options.discount : subtotal;
}

function canRefund(order: Order): boolean {
  const daysSinceOrder = (Date.now() - order.createdAt.getTime()) / (1000 * 60 * 60 * 24);
  return order.status === 'completed' && daysSinceOrder <= 30;
}

// Generic test structure (works with any test framework)
// Test: calculateOrderTotal
// - Input: [{ price: 100, quantity: 2 }, { price: 50, quantity: 1 }]
// - Expected: 250
// - Input: [{ price: 100, quantity: 1 }], { discount: 10 }
// - Expected: 90

// Test: canRefund
// - Input: { status: 'completed', createdAt: 15 days ago }
// - Expected: true
// - Input: { status: 'completed', createdAt: 45 days ago }
// - Expected: false
```

### Layer 2: Application Logic (Unit Tests)

Test stateful logic (hooks, stores, composables) in isolation.

```typescript
// Generic stateful logic - framework-agnostic interface
interface CartLogic {
  items: CartItem[];
  totalPrice: number;
  itemCount: number;
  addItem(item: CartItem): void;
  removeItem(id: string): void;
  clear(): void;
}

// Implementation can use any state management
class CartLogicImpl implements CartLogic {
  private _items: CartItem[] = [];

  get items() { return this._items; }
  get totalPrice() {
    return this._items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  }
  get itemCount() {
    return this._items.reduce((sum, item) => sum + item.quantity, 0);
  }

  addItem(item: CartItem) {
    this._items.push(item);
  }

  removeItem(id: string) {
    this._items = this._items.filter(item => item.id !== id);
  }

  clear() {
    this._items = [];
  }
}

// Test pattern (framework-agnostic)
// 1. Create instance
// 2. Call addItem({ id: 'item-1', price: 100, quantity: 1 })
// 3. Assert items.length === 1
// 4. Assert totalPrice === 100
```

### Layer 3: Adapters (Contract Tests)

Verify external API responses match expected schemas.

```typescript
// Schema definition (using Zod, but could be any validator)
const OrderSchema = z.object({
  id: z.string(),
  status: z.enum(['pending', 'completed', 'cancelled']),
  items: z.array(z.object({
    productId: z.string(),
    quantity: z.number()
  })),
  total: z.number()
});

// Adapter interface
interface OrderApi {
  getOrder(id: string): Promise<Order>;
  createOrder(command: CreateOrderCommand): Promise<Order>;
}

// Test pattern:
// 1. Call api.getOrder('order-123')
// 2. Parse response with OrderSchema
// 3. Assert parsing succeeds
// 4. If parsing fails, API contract is broken
```

### Layer 4: Workflows (Integration Tests)

Test multi-step processes with mocked external dependencies.

```typescript
// Workflow orchestrates multiple adapters
async function processCheckout(
  cmd: CheckoutCommand,
  ctx: Context,
  adapters: {
    payment: PaymentAdapter;
    inventory: InventoryAdapter;
    notification: NotificationAdapter;
  }
): Promise<CheckoutResult> {
  // Step 1: Reserve inventory
  await adapters.inventory.reserve(cmd.items);

  // Step 2: Process payment
  const payment = await adapters.payment.charge(cmd.amount);

  // Step 3: Send confirmation
  await adapters.notification.send(cmd.userId, 'Order confirmed');

  return { success: true, paymentId: payment.id };
}

// Test pattern (using dependency injection):
// 1. Create mock adapters (return predefined values)
// 2. Call processCheckout with mocks
// 3. Verify mocks were called with correct arguments
// 4. Test compensation: if payment fails, inventory is released
```

## Implementation Examples

### Example 1: Jest (JavaScript/TypeScript)

```typescript
// Domain unit tests
describe('Order Rules', () => {
  describe('calculateOrderTotal', () => {
    it('sums item prices with quantities', () => {
      const items = [
        { price: 100, quantity: 2 },
        { price: 50, quantity: 1 },
      ];
      expect(calculateOrderTotal(items)).toBe(250);
    });

    it('applies discount correctly', () => {
      const items = [{ price: 100, quantity: 1 }];
      expect(calculateOrderTotal(items, { discount: 10 })).toBe(90);
    });
  });
});

// Integration tests with mocks
describe('Checkout Saga', () => {
  let mockPayment: jest.Mock;
  let mockInventory: jest.Mock;

  beforeEach(() => {
    mockPayment = jest.fn().mockResolvedValue({ txId: 'tx-123' });
    mockInventory = jest.fn().mockResolvedValue(true);
  });

  it('completes full checkout flow', async () => {
    const cmd = { items: [{ id: '1', qty: 2 }], amount: 200 };
    const result = await processCheckout(cmd, context, {
      payment: mockPayment,
      inventory: mockInventory,
    });

    expect(result.success).toBe(true);
    expect(mockPayment).toHaveBeenCalledWith(200);
    expect(mockInventory).toHaveBeenCalledWith(cmd.items);
  });
});
```

### Example 2: Vitest (JavaScript/TypeScript)

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Domain unit tests (same as Jest)
describe('Order Rules', () => {
  it('calculates total correctly', () => {
    const items = [{ price: 100, quantity: 2 }];
    expect(calculateOrderTotal(items)).toBe(200);
  });
});

// Integration tests with Vitest mocks
describe('Checkout Saga', () => {
  let mockPayment: any;

  beforeEach(() => {
    mockPayment = vi.fn().mockResolvedValue({ txId: 'tx-123' });
  });

  it('processes payment', async () => {
    const result = await processCheckout(cmd, context, {
      payment: mockPayment
    });

    expect(mockPayment).toHaveBeenCalled();
    expect(result.success).toBe(true);
  });
});
```

### Example 3: Pytest (Python)

```python
# Domain unit tests
def test_calculate_order_total():
    items = [
        {"price": 100, "quantity": 2},
        {"price": 50, "quantity": 1}
    ]
    assert calculate_order_total(items) == 250

def test_calculate_total_with_discount():
    items = [{"price": 100, "quantity": 1}]
    assert calculate_order_total(items, discount=10) == 90

# Integration tests with pytest fixtures
@pytest.fixture
def mock_payment(mocker):
    return mocker.Mock(return_value={"tx_id": "tx-123"})

@pytest.fixture
def mock_inventory(mocker):
    return mocker.Mock(return_value=True)

def test_checkout_flow(mock_payment, mock_inventory):
    cmd = CheckoutCommand(items=[...], amount=200)
    result = process_checkout(cmd, context, {
        "payment": mock_payment,
        "inventory": mock_inventory
    })

    assert result["success"] is True
    mock_payment.assert_called_once_with(200)
    mock_inventory.assert_called_once()
```

### Example 4: React Testing Library (Framework-Specific)

```typescript
import { renderHook, act } from '@testing-library/react';
import { useCartLogic } from './useCartLogic';

// Testing React hooks
describe('useCartLogic', () => {
  it('adds items correctly', () => {
    const { result } = renderHook(() => useCartLogic());

    act(() => {
      result.current.addItem({ id: 'item-1', price: 100, quantity: 1 });
    });

    expect(result.current.items).toHaveLength(1);
    expect(result.current.totalPrice).toBe(100);
  });

  it('calculates total with multiple items', () => {
    const { result } = renderHook(() => useCartLogic());

    act(() => {
      result.current.addItem({ id: 'item-1', price: 100, quantity: 2 });
      result.current.addItem({ id: 'item-2', price: 50, quantity: 1 });
    });

    expect(result.current.totalPrice).toBe(250);
  });
});
```

## Coverage Guidelines

| Layer | Coverage Target | Test Type |
|-------|-----------------|-----------|
| `01_domains/` | 100% | Unit |
| `headless/` | 90%+ | Unit |
| `adapters/` | Schema coverage | Contract |
| `workflows/` | All paths | Integration |
| `views/` | Critical paths | Snapshot/E2E |

## Refactoring Safety Patterns

Tests that enable confident refactoring without breaking existing behavior.

### 1. Characterization Tests

Document existing behavior before refactoring legacy code:

```typescript
// Before refactoring: Capture current behavior
describe('Legacy calculatePrice (characterization)', () => {
  it('characterizes behavior for standard cart', () => {
    const cart = {
      items: [
        { price: 100, quantity: 2 },
        { price: 50, quantity: 1 }
      ],
      discount: 0.1
    };

    const result = calculatePrice(cart);

    // Document exact current behavior (even if wrong)
    expect(result).toBe(225);  // (100*2 + 50*1) * 0.9
  });

  it('characterizes edge case: empty cart', () => {
    expect(calculatePrice({ items: [], discount: 0 })).toBe(0);
  });

  it('characterizes edge case: 100% discount', () => {
    const cart = { items: [{ price: 100, quantity: 1 }], discount: 1.0 };
    expect(calculatePrice(cart)).toBe(0);
  });

  it('characterizes bug: negative quantity (current behavior)', () => {
    const cart = { items: [{ price: 100, quantity: -1 }], discount: 0 };
    // Current code allows this - capture as-is
    expect(calculatePrice(cart)).toBe(-100);
  });
});

// After refactoring: Same tests pass with new implementation
describe('Refactored calculatePrice', () => {
  // Tests remain identical - validates refactoring preserved behavior
  it('maintains behavior for standard cart', () => {
    const cart = createCart([
      createItem(100, 2),
      createItem(50, 1)
    ], 0.1);

    expect(calculatePrice(cart)).toBe(225);
  });
});
```

### 2. Golden Master Testing

Compare outputs before and after refactoring:

```typescript
// Generate golden master from current implementation
function generateGoldenMaster() {
  const testCases = [
    { input: cart1, output: calculatePrice(cart1) },
    { input: cart2, output: calculatePrice(cart2) },
    // ... 100s of test cases
  ];

  fs.writeFileSync('goldenMaster.json', JSON.stringify(testCases));
}

// Validate refactored code against golden master
describe('calculatePrice (golden master)', () => {
  const goldenMaster = JSON.parse(fs.readFileSync('goldenMaster.json', 'utf-8'));

  goldenMaster.forEach(({ input, output }, index) => {
    it(`matches golden master case ${index}`, () => {
      expect(calculatePrice(input)).toBe(output);
    });
  });
});
```

### 3. Approval Testing

Snapshot entire complex outputs for refactoring validation:

```typescript
describe('OrderSummaryGenerator (approval tests)', () => {
  it('generates summary for complex order', () => {
    const order = createComplexOrder();

    const summary = OrderSummaryGenerator.generate(order);

    // Snapshot complex nested structure
    expect(summary).toMatchSnapshot();
    /*
    Snapshot will include:
    - Order details
    - Line items with calculations
    - Tax breakdowns
    - Shipping information
    - Totals and discounts
    */
  });

  it('generates summary with multiple payment methods', () => {
    const order = createOrderWithSplitPayment();

    expect(OrderSummaryGenerator.generate(order)).toMatchSnapshot();
  });
});

// After refactoring: Run tests, review snapshot diffs
// Approve new snapshots if changes are intentional
```

### 4. Mutation Testing

Validate that tests actually catch logic changes:

```typescript
// Example mutation testing configuration (using Stryker)
// stryker.conf.json
{
  "mutate": [
    "src/domains/**/*.ts",
    "!src/domains/**/*.test.ts"
  ],
  "testRunner": "jest",
  "coverageAnalysis": "perTest",
  "thresholds": {
    "high": 80,
    "low": 60,
    "break": 50
  }
}

// Original code
function applyDiscount(price: number, discount: number): number {
  return price * (1 - discount);
}

// Mutation: Changes operator - (minus) to + (plus)
function applyDiscount(price: number, discount: number): number {
  return price * (1 + discount);  // Mutant
}

// Test must FAIL for this mutation (otherwise weak test)
describe('applyDiscount (mutation coverage)', () => {
  it('applies 10% discount correctly', () => {
    expect(applyDiscount(100, 0.1)).toBe(90);
    // If this test passes with mutation, it's not catching the bug
  });

  it('applies 0% discount (no change)', () => {
    expect(applyDiscount(100, 0)).toBe(100);
    // This test WILL catch the mutation
  });

  it('applies 100% discount (free)', () => {
    expect(applyDiscount(100, 1.0)).toBe(0);
    // This test WILL catch the mutation
  });
});
```

### 5. Behavior-Focused Tests

Test behavior, not implementation details:

```typescript
// ❌ BAD - Tests implementation details
describe('UserService (implementation-focused)', () => {
  it('calls repository.findById with correct ID', () => {
    const repo = { findById: jest.fn() };
    const service = new UserService(repo);

    service.getUser('user-123');

    expect(repo.findById).toHaveBeenCalledWith('user-123');
    // Breaks when refactoring to use findByQuery
  });
});

// ✅ GOOD - Tests behavior
describe('UserService (behavior-focused)', () => {
  it('returns user when user exists', async () => {
    const repo = createTestRepo({
      users: [{ id: 'user-123', name: 'Alice' }]
    });
    const service = new UserService(repo);

    const user = await service.getUser('user-123');

    expect(user).toEqual({ id: 'user-123', name: 'Alice' });
    // Survives refactoring as long as behavior is same
  });

  it('throws NotFoundError when user does not exist', async () => {
    const repo = createTestRepo({ users: [] });
    const service = new UserService(repo);

    await expect(service.getUser('nonexistent')).rejects.toThrow(NotFoundError);
    // Behavior-focused: Tests outcome, not how
  });
});
```

### Refactoring Workflow with Tests

**Step-by-step safe refactoring:**

```typescript
// Step 1: Add characterization tests for existing code
describe('Legacy code (before refactoring)', () => {
  // Capture all current behavior
});

// Step 2: Refactor incrementally
// - Extract method
// - Rename variables
// - Simplify logic
// - Each step: run tests

// Step 3: Add new behavior-focused tests
describe('Refactored code (new tests)', () => {
  // Better test structure, same behavior
});

// Step 4: Remove characterization tests (optional)
// - If new tests cover same ground
// - Keep if documenting tricky edge cases

// Step 5: Run mutation testing
// - Verify tests catch logic errors
// - Add tests for surviving mutations
```

### When to Use Each Pattern

**Characterization Tests** - Use when:
- Refactoring legacy code with poor/no tests
- Behavior is complex and poorly documented
- Need safety net before making changes

**Golden Master** - Use when:
- Output is deterministic
- Large number of edge cases exist
- Complex calculations or transformations

**Approval Testing** - Use when:
- Output is complex nested data
- Visual/structural changes need review
- Refactoring report generators, formatters

**Mutation Testing** - Use when:
- Validating test suite quality
- Critical business logic needs robust tests
- After major refactoring to ensure safety

**Behavior-Focused Tests** - Always use:
- Default test style for all new code
- Enables fearless refactoring
- Survives implementation changes

## Good Example

```typescript
// ✅ Layer-appropriate testing

// Domain: Pure unit test (framework-agnostic)
test('calculateTax applies correct rate', () => {
  const result = calculateTax(100, 'CA');
  assert(result === 7.25);
});

// Application Logic: Stateful logic test
test('Cart updates total on add', () => {
  const cart = new CartLogic();
  cart.addItem({ id: '1', price: 100, quantity: 1 });
  assert(cart.totalPrice === 100);
});

// Adapter: Contract test
test('API response matches schema', async () => {
  const data = await api.fetch();
  const parseResult = Schema.safeParse(data);
  assert(parseResult.success === true);
});

// Workflow: Integration test with mocks
test('checkout compensates on payment failure', async () => {
  const mockPayment = createMock(() => { throw new Error('Failed'); });
  const mockInventory = createMock(() => true);

  await expect(
    processCheckout(cmd, { payment: mockPayment, inventory: mockInventory })
  ).rejects.toThrow('Failed');

  // Verify inventory was not reserved (or rolled back)
  assert(mockInventory.notCalled());
});
```

## Bad Example

```typescript
// ❌ E2E test for business logic
test('order total calculation', async () => {
  await browser.goto('/cart');
  await browser.click('#add-item');
  await browser.click('#add-item');
  // Slow, brittle, tests infrastructure not logic
  expect(await browser.getText('#total')).toBe('$200');
});

// ❌ No contract test for API
test('fetch user', async () => {
  const user = await api.getUser('123');
  expect(user.name).toBe('John');  // Doesn't verify schema
});
```

## Anti-Patterns

1. **E2E tests for logic**
   ```typescript
   // ❌ Use unit tests instead
   it('validates email format', async () => {
     await page.type('#email', 'invalid');
     // ...browser automation for simple validation
   });
   ```

2. **No contract tests**
   ```typescript
   // ❌ API changes break app silently
   const data = await api.fetch();
   // No schema validation
   ```

3. **Mocking everything**
   ```typescript
   // ❌ Over-mocking loses integration confidence
   jest.mock('./database');
   jest.mock('./cache');
   jest.mock('./api');
   // What are we even testing?
   ```

## Checklist

- [ ] Domain layer has 100% unit test coverage (pure functions)
- [ ] Application logic has unit tests (stateful logic, framework-specific)
- [ ] Adapters have contract/schema tests
- [ ] Workflows have integration tests with mocked dependencies
- [ ] E2E tests cover only critical user journeys
- [ ] Test framework chosen appropriate for tech stack (Jest, Vitest, Pytest, etc.)
- [ ] Mock factories generate from schemas (Pillar C)
- [ ] Characterization tests exist for legacy code before refactoring
- [ ] Mutation testing validates test quality for critical paths
- [ ] Snapshot tests verify refactoring safety for complex outputs
- [ ] Test coverage prevents regression during refactoring

## References

- Related: Pillar C (Mocking) - test data generation
- Related: Pillar M (Saga) - test compensation
- Pattern: Testing Pyramid, Contract Testing
- Template: `.claude/pillars/pillar-k/testing.ts`
- Checklist: `.claude/pillars/pillar-k/checklist.md`

## Changelog

### Version 2.1.0 (2026-03-14)

**Issue**: #195 - Phase 2: Integrate missing best practices

**Changes**:
- ✅ Added comprehensive "Refactoring Safety Patterns" section
- ✅ Covered 5 testing patterns for safe refactoring:
  - Characterization tests for legacy code
  - Golden master testing for deterministic outputs
  - Approval testing for complex nested structures
  - Mutation testing for test quality validation
  - Behavior-focused tests for implementation independence
- ✅ Added step-by-step refactoring workflow with tests
- ✅ Showed when to use each pattern
- ✅ Added refactoring safety checklist items

**Impact**:
- Refactoring Safety best practice now covered (Testing/Maintainability category)
- Developers have clear patterns for confident refactoring
- Reduces regression risk during code improvements
- Enables safe evolution of legacy code

**Backward compatibility**: All existing content preserved, purely additive change

##

### Version 2.0.0 (2026-03-14)

**Issue**: #194 - Remove tech-stack dependencies

**Changes**:
- ✅ Added framework-agnostic testing pyramid principles
- ✅ Created generic test patterns for each layer (domain, application, adapters, workflows)
- ✅ Replaced React Testing Library-specific examples with multi-framework examples:
  - Example 1: Jest (JavaScript/TypeScript)
  - Example 2: Vitest (JavaScript/TypeScript)
  - Example 3: Pytest (Python)
  - Example 4: React Testing Library (framework-specific)
- ✅ All framework-specific code moved to clearly labeled "Implementation Examples" section

**Impact**:
- Testing strategy now applicable to ANY tech stack
- Coverage guidelines work for Python, Go, Rust, etc.
- Developers see testing patterns across multiple ecosystems

**Backward compatibility**: React Testing Library example preserved, now labeled as framework-specific
