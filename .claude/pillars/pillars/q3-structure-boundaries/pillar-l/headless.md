# Pillar L: Headless Abstraction

> Separate business logic from UI presentation

## Rule

Business logic must be separated from UI rendering:
- **Headless Layer**: Framework primitives allowed, JSX **FORBIDDEN**
- **View Layer**: Renders UI, delegates logic to headless hooks

## Purpose

- Enable logic reuse across different UIs
- Test logic without DOM/rendering
- Clear separation of concerns
- Support multiple frontends (web, mobile, CLI)

## Core Concept

Separate **what to display** (data, state, logic) from **how to display it** (rendering, styling, DOM). This enables:
- Logic reuse across different UIs
- Testing without rendering
- Multiple presentations of the same logic

**Key Principle**: Create a "headless" layer that exposes an interface for state and actions, consumed by a thin presentation layer.

## Generic Implementation (Framework-Agnostic)

### Layer Separation

```
┌─────────────────────────────────────────────────────────┐
│ HEADLESS LAYER (Logic)                                   │
│                                                          │
│ ✅ Allowed:                                              │
│    • Framework state primitives (hooks, composables, etc)│
│    • Business logic                                      │
│    • State management                                    │
│    • API calls                                          │
│    • Data transformations                                │
│                                                          │
│ ❌ Forbidden:                                            │
│    • Templates / JSX / HTML                              │
│    • CSS / Styling                                       │
│    • DOM manipulation                                    │
│    • Rendering logic                                     │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Returns: { data, state, actions }
                         ▼
┌─────────────────────────────────────────────────────────┐
│ VIEW LAYER (Presentation)                                │
│                                                          │
│ ✅ Allowed:                                              │
│    • Templates / JSX / HTML                              │
│    • CSS / Styling                                       │
│    • Layout components                                   │
│    • Event handlers (calling headless actions)           │
│                                                          │
│ ❌ Forbidden:                                            │
│    • Business logic                                      │
│    • Complex state management                            │
│    • Direct API calls                                    │
│    • Data transformation                                 │
└─────────────────────────────────────────────────────────┘
```

### Headless Interface Pattern

Define a clear interface for the headless layer:

```typescript
// Generic headless logic interface (framework-agnostic)
type SearchState =
  | { status: 'idle' }
  | { status: 'searching'; query: string }
  | { status: 'success'; products: Product[] }
  | { status: 'error'; error: string };

interface ProductSearchLogic {
  // Current state
  state: SearchState;

  // Derived data
  products: Product[];
  isSearching: boolean;
  hasResults: boolean;
  resultCount: number;
  error: string | null;

  // Actions
  search(query: string): Promise<void>;
  clear(): void;
  selectProduct(id: ProductId): void;
}
```

### Generic Implementation Pattern

```typescript
// Core logic - works with any state management approach
class ProductSearchLogicImpl implements ProductSearchLogic {
  private _state: SearchState = { status: 'idle' };
  private listeners: Array<() => void> = [];

  get state() { return this._state; }
  get products() {
    return this._state.status === 'success' ? this._state.products : [];
  }
  get isSearching() { return this._state.status === 'searching'; }
  get hasResults() { return this.products.length > 0; }
  get resultCount() { return this.products.length; }
  get error() {
    return this._state.status === 'error' ? this._state.error : null;
  }

  async search(query: string) {
    if (!query.trim()) {
      this.setState({ status: 'idle' });
      return;
    }

    this.setState({ status: 'searching', query });

    try {
      const products = await productApi.search(query);
      this.setState({ status: 'success', products });
    } catch (error) {
      this.setState({
        status: 'error',
        error: error instanceof Error ? error.message : 'Search failed'
      });
    }
  }

  clear() {
    this.setState({ status: 'idle' });
  }

  selectProduct(id: ProductId) {
    // Selection logic...
  }

  private setState(newState: SearchState) {
    this._state = newState;
    this.notify();
  }

  private notify() {
    this.listeners.forEach(listener => listener());
  }

  // Subscribe for state changes (used by UI frameworks)
  subscribe(listener: () => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
}
```

## Implementation Examples

### Example 1: React (Hooks)

```typescript
// headless/useProductSearch.ts - React implementation
import { useState, useCallback } from 'react';
import { productApi } from '../adapters/productApi';

export function useProductSearch(): ProductSearchLogic {
  const [state, setState] = useState<SearchState>({ status: 'idle' });

  const search = useCallback(async (query: string) => {
    if (!query.trim()) {
      setState({ status: 'idle' });
      return;
    }

    setState({ status: 'searching', query });

    try {
      const products = await productApi.search(query);
      setState({ status: 'success', products });
    } catch (error) {
      setState({
        status: 'error',
        error: error instanceof Error ? error.message : 'Search failed'
      });
    }
  }, []);

  const clear = useCallback(() => {
    setState({ status: 'idle' });
  }, []);

  // Derived values
  const products = state.status === 'success' ? state.products : [];

  return {
    state,
    products,
    isSearching: state.status === 'searching',
    error: state.status === 'error' ? state.error : null,
    hasResults: products.length > 0,
    resultCount: products.length,
    search,
    clear,
    selectProduct: (id) => { /* ... */ }
  };
}

// View component
export function ProductSearchView() {
  const logic = useProductSearch();

  return (
    <div>
      <SearchInput onSearch={logic.search} />
      {logic.isSearching && <Spinner />}
      {logic.hasResults && logic.products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
      {logic.error && <ErrorMessage>{logic.error}</ErrorMessage>}
    </div>
  );
}
```

### Example 2: Vue 3 (Composables)

```typescript
// headless/useProductSearch.ts - Vue implementation
import { ref, computed } from 'vue';
import { productApi } from '../adapters/productApi';

export function useProductSearch(): ProductSearchLogic {
  const state = ref<SearchState>({ status: 'idle' });

  const search = async (query: string) => {
    if (!query.trim()) {
      state.value = { status: 'idle' };
      return;
    }

    state.value = { status: 'searching', query };

    try {
      const products = await productApi.search(query);
      state.value = { status: 'success', products };
    } catch (error) {
      state.value = {
        status: 'error',
        error: error instanceof Error ? error.message : 'Search failed'
      };
    }
  };

  const clear = () => {
    state.value = { status: 'idle' };
  };

  // Computed derived values
  const products = computed(() =>
    state.value.status === 'success' ? state.value.products : []
  );
  const isSearching = computed(() => state.value.status === 'searching');
  const hasResults = computed(() => products.value.length > 0);

  return {
    state,
    products,
    isSearching,
    hasResults,
    resultCount: computed(() => products.value.length),
    error: computed(() =>
      state.value.status === 'error' ? state.value.error : null
    ),
    search,
    clear,
    selectProduct: (id) => { /* ... */ }
  };
}

// Vue component template:
// <template>
//   <div>
//     <SearchInput @search="logic.search" />
//     <Spinner v-if="logic.isSearching" />
//     <ProductCard
//       v-for="product in logic.products"
//       :key="product.id"
//       :product="product"
//     />
//     <ErrorMessage v-if="logic.error">{{ logic.error }}</ErrorMessage>
//   </div>
// </template>
```

### Example 3: Svelte (Stores)

```typescript
// headless/productSearch.ts - Svelte implementation
import { writable, derived } from 'svelte/store';
import { productApi } from '../adapters/productApi';

export function createProductSearch(): ProductSearchLogic {
  const state = writable<SearchState>({ status: 'idle' });

  const search = async (query: string) => {
    if (!query.trim()) {
      state.set({ status: 'idle' });
      return;
    }

    state.set({ status: 'searching', query });

    try {
      const products = await productApi.search(query);
      state.set({ status: 'success', products });
    } catch (error) {
      state.set({
        status: 'error',
        error: error instanceof Error ? error.message : 'Search failed'
      });
    }
  };

  const clear = () => state.set({ status: 'idle' });

  // Derived stores
  const products = derived(state, $state =>
    $state.status === 'success' ? $state.products : []
  );
  const isSearching = derived(state, $state => $state.status === 'searching');

  return {
    subscribe: state.subscribe,  // Svelte store contract
    state,
    products,
    isSearching,
    hasResults: derived(products, $products => $products.length > 0),
    resultCount: derived(products, $products => $products.length),
    error: derived(state, $state =>
      $state.status === 'error' ? $state.error : null
    ),
    search,
    clear,
    selectProduct: (id) => { /* ... */ }
  };
}

// Svelte component:
// <script>
//   const logic = createProductSearch();
//   $: state = $logic.state;
// </script>
//
// <div>
//   <SearchInput on:search={(e) => logic.search(e.detail)} />
//   {#if $logic.isSearching}
//     <Spinner />
//   {/if}
//   {#each $logic.products as product}
//     <ProductCard {product} />
//   {/each}
// </div>
```

### Example 4: Backend/CLI (Node.js)

```typescript
// Headless pattern works for backends too!
// Example: CLI search interface

import { ProductSearchLogicImpl } from './ProductSearchLogicImpl';

async function runCLI() {
  const searchLogic = new ProductSearchLogicImpl();

  // Subscribe to state changes
  searchLogic.subscribe(() => {
    console.clear();
    console.log(`Status: ${searchLogic.state.status}`);

    if (searchLogic.isSearching) {
      console.log('Searching...');
    }

    if (searchLogic.hasResults) {
      console.log(`Found ${searchLogic.resultCount} products:`);
      searchLogic.products.forEach(p => {
        console.log(`  - ${p.name} ($${p.price})`);
      });
    }

    if (searchLogic.error) {
      console.error(`Error: ${searchLogic.error}`);
    }
  });

  // Interactive CLI
  const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  });

  readline.on('line', async (input: string) => {
    await searchLogic.search(input);
  });
}
```

### View Component (React - for reference)

```typescript
// This section moved to Example 1 above
export function ProductSearchView() {
  const {
    products,
    isSearching,
    error,
    hasResults,
    resultCount,
    search,
    clear,
  } = useProductSearch();

  return (
    <div className="product-search">
      <SearchInput
        onSearch={search}
        onClear={clear}
        isLoading={isSearching}
      />

      {error && <div className="error">{error}</div>}

      {hasResults && (
        <>
          <p>{resultCount} products found</p>
          <div className="product-grid">
            {products.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </>
      )}

      {!hasResults && !isSearching && (
        <p>No products found</p>
      )}
    </div>
  );
}
```

### Testing Headless Logic

```typescript
// headless/useProductSearch.test.ts
import { renderHook, act, waitFor } from '@testing-library/react';
import { useProductSearch } from './useProductSearch';

// No DOM needed!
describe('useProductSearch', () => {
  it('starts in idle state', () => {
    const { result } = renderHook(() => useProductSearch());
    expect(result.current.state.status).toBe('idle');
  });

  it('searches and returns products', async () => {
    const { result } = renderHook(() => useProductSearch());

    act(() => {
      result.current.search('laptop');
    });

    expect(result.current.isSearching).toBe(true);

    await waitFor(() => {
      expect(result.current.state.status).toBe('success');
    });

    expect(result.current.hasResults).toBe(true);
  });
});
```

## Good Example

```typescript
// ✅ Clean separation

// headless/useCart.ts - Logic only
export function useCart() {
  const [items, setItems] = useState<CartItem[]>([]);

  const addItem = (item: CartItem) => { /* logic */ };
  const removeItem = (id: ItemId) => { /* logic */ };
  const total = items.reduce((sum, i) => sum + i.price, 0);

  return { items, addItem, removeItem, total };
  // Returns data/functions, NO JSX
}

// views/CartView.tsx - Presentation only
export function CartView() {
  const { items, removeItem, total } = useCart();

  return (
    <div>
      {items.map(item => (
        <CartItemRow
          key={item.id}
          item={item}
          onRemove={() => removeItem(item.id)}
        />
      ))}
      <p>Total: ${total}</p>
    </div>
  );
}
```

## Bad Example

```typescript
// ❌ Logic and UI mixed in hook
function useCart() {
  const [items, setItems] = useState([]);

  // ❌ JSX in headless hook!
  const renderItem = (item) => (
    <div className="item">
      <span>{item.name}</span>
      <button onClick={() => remove(item.id)}>X</button>
    </div>
  );

  // ❌ Returning JSX
  return { items, renderItem };
}

// ❌ Logic in view component
function CartView() {
  const [items, setItems] = useState([]);

  // ❌ Business logic in view
  const calculateDiscount = () => {
    if (items.length > 5) return 0.1;
    return 0;
  };

  // ❌ API call in view
  useEffect(() => {
    fetch('/api/cart').then(/* ... */);
  }, []);

  return <div>...</div>;
}
```

## Anti-Patterns

1. **JSX in headless hooks**
   ```typescript
   // ❌ Hooks should not return JSX
   return { renderButton: () => <Button /> };
   ```

2. **Business logic in views**
   ```typescript
   // ❌ Views should only render
   const discount = items.length > 5 ? 0.1 : 0;
   ```

3. **Direct API calls in views**
   ```typescript
   // ❌ Use headless hook or adapter
   useEffect(() => { fetch('/api/...') }, []);
   ```

4. **Styling logic in headless**
   ```typescript
   // ❌ Styling is presentation concern
   const buttonClass = isActive ? 'btn-active' : 'btn';
   ```

## Exceptions

- Simple presentational components without logic
- Third-party component wrappers

## Checklist

- [ ] Headless files contain NO JSX/HTML
- [ ] Views delegate all logic to headless hooks
- [ ] Headless hooks are unit testable without DOM
- [ ] Business calculations in headless, not views
- [ ] API calls through adapters, called from headless
- [ ] State management in headless hooks

## References

- Related: Pillar D (FSM) - state in headless
- Related: Pillar K (Testing) - test headless separately
- Pattern: Headless UI, Render Props, Compound Components

## Assets

- Template: `.claude/pillars/pillar-l/headless.ts`
- Checklist: `.claude/pillars/pillar-l/checklist.md`
- Audit: `.claude/pillars/pillar-l/audit.ts`

## Changelog

### Version 2.0.0 (2026-03-14)

**Issue**: #194 - Remove tech-stack dependencies

**Changes**:
- ✅ Added framework-agnostic headless pattern principles
- ✅ Created generic business logic interface (ProductSearchLogic)
- ✅ Replaced React hooks-specific implementation with multi-framework examples:
  - Example 1: React (useState/useCallback hooks)
  - Example 2: Vue 3 (ref/computed composables)
  - Example 3: Svelte (writable/derived stores)
  - Example 4: Node.js/CLI (class-based with listeners)
- ✅ All framework-specific code moved to clearly labeled "Implementation Examples" section

**Impact**:
- Headless pattern now applicable to ANY UI framework
- Developers see how to separate logic from presentation in their framework
- Backend developers can apply same pattern for CLI tools

**Backward compatibility**: React example preserved, now one of four framework options
