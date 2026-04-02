# Pillar D: Explicit Finite State Machines

> Eliminate impossible states through union types

## Rule

Asynchronous flows must **NEVER** rely on boolean flags (`isLoading`, `isError`). Use explicit union types for state.

## Purpose

Mathematically prevent impossible states:
- `isLoading: true` AND `isError: true` (impossible!)
- `isSuccess: true` AND `isLoading: true` (impossible!)
- Undefined behavior when multiple flags are true

## Core Concept

Asynchronous operations transition through discrete, mutually exclusive states. Use discriminated unions to make impossible state combinations literally unrepresentable.

**Key Principle**: Replace multiple boolean flags with a single state variable using union types.

## Generic Implementation (TypeScript)

### State as Discriminated Union

```typescript
// ✅ GOOD: Explicit FSM - Tech-stack independent
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string };

// Impossible states are literally impossible to represent:
// - Can't be loading AND have error
// - Can't be idle AND have data
// TypeScript enforces this at compile time
```

### State Machine with Actions

```typescript
type State<T> =
  | { status: 'idle'; items: T[] }
  | { status: 'loading'; items: T[] }
  | { status: 'success'; items: T[]; message: string }
  | { status: 'error'; items: T[]; error: string };

type Action<T> =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; items: T[] }
  | { type: 'FETCH_ERROR'; error: string };

// Pure reducer function - no framework dependencies
function transition<T>(state: State<T>, action: Action<T>): State<T> {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, status: 'loading' };
    case 'FETCH_SUCCESS':
      return { status: 'success', items: action.items, message: 'Loaded' };
    case 'FETCH_ERROR':
      return { ...state, status: 'error', error: action.error };
    default:
      return state;
  }
}
```

### Pattern Matching on State

```typescript
// Generic function to handle different states
function handleState<T>(state: State<T>): void {
  // TypeScript narrows the type in each branch
  switch (state.status) {
    case 'idle':
      console.log('Ready to fetch');
      break;
    case 'loading':
      console.log('Fetching...');
      break;
    case 'success':
      console.log(`Loaded ${state.items.length} items`); // items guaranteed
      break;
    case 'error':
      console.error(state.error); // error guaranteed
      break;
  }
}
```

## Implementation Examples

### Example 1: React (Frontend)

```typescript
import { useReducer } from 'react';

function UserListComponent() {
  const [state, dispatch] = useReducer(transition, {
    status: 'idle',
    items: []
  });

  const fetchUsers = () => {
    dispatch({ type: 'FETCH_START' });
    fetch('/api/users')
      .then(res => res.json())
      .then(data => dispatch({ type: 'FETCH_SUCCESS', items: data }))
      .catch(err => dispatch({ type: 'FETCH_ERROR', error: err.message }));
  };

  // TypeScript narrows the type in each branch
  switch (state.status) {
    case 'idle':
      return <button onClick={fetchUsers}>Load Users</button>;
    case 'loading':
      return <div>Loading...</div>;
    case 'success':
      return <ul>{state.items.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
    case 'error':
      return <div>Error: {state.error}</div>;
  }
}
```

### Example 2: Vue 3 (Frontend)

```typescript
import { ref, computed } from 'vue';

// Vue composable using FSM
function useRequestState<T>() {
  const state = ref<State<T>>({ status: 'idle', items: [] });

  const dispatch = (action: Action<T>) => {
    state.value = transition(state.value, action);
  };

  const isLoading = computed(() => state.value.status === 'loading');
  const items = computed(() =>
    state.value.status === 'success' ? state.value.items : []
  );

  return { state, dispatch, isLoading, items };
}

// In Vue component template:
// <template>
//   <div v-if="state.status === 'idle'">
//     <button @click="fetch">Load</button>
//   </div>
//   <div v-else-if="state.status === 'loading'">Loading...</div>
//   <ul v-else-if="state.status === 'success'">
//     <li v-for="item in state.items" :key="item.id">{{ item.name }}</li>
//   </ul>
//   <div v-else-if="state.status === 'error'">Error: {{ state.error }}</div>
// </template>
```

### Example 3: Svelte (Frontend)

```typescript
import { writable } from 'svelte/store';

// Svelte store using FSM
function createRequestStore<T>() {
  const { subscribe, set, update } = writable<State<T>>({
    status: 'idle',
    items: []
  });

  return {
    subscribe,
    dispatch: (action: Action<T>) => update(state => transition(state, action)),
    reset: () => set({ status: 'idle', items: [] })
  };
}

// In Svelte component:
// <script>
//   const store = createRequestStore();
//   $: state = $store;
// </script>
//
// {#if state.status === 'idle'}
//   <button on:click={() => store.dispatch({ type: 'FETCH_START' })}>Load</button>
// {:else if state.status === 'loading'}
//   <p>Loading...</p>
// {:else if state.status === 'success'}
//   <ul>
//     {#each state.items as item}
//       <li>{item.name}</li>
//     {/each}
//   </ul>
// {:else if state.status === 'error'}
//   <p>Error: {state.error}</p>
// {/if}
```

### Example 4: Node.js (Backend)

```typescript
// Backend API request handler using FSM
class RequestHandler<T> {
  private state: State<T> = { status: 'idle', items: [] };

  async execute(fetchFn: () => Promise<T[]>): Promise<State<T>> {
    this.dispatch({ type: 'FETCH_START' });

    try {
      const items = await fetchFn();
      this.dispatch({ type: 'FETCH_SUCCESS', items });
    } catch (error) {
      this.dispatch({
        type: 'FETCH_ERROR',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }

    return this.state;
  }

  private dispatch(action: Action<T>) {
    this.state = transition(this.state, action);
    this.logState();
  }

  private logState() {
    switch (this.state.status) {
      case 'idle':
        console.log('Handler ready');
        break;
      case 'loading':
        console.log('Fetching data...');
        break;
      case 'success':
        console.log(`Fetched ${this.state.items.length} items`);
        break;
      case 'error':
        console.error(`Error: ${this.state.error}`);
        break;
    }
  }
}

// Usage
const handler = new RequestHandler<User>();
const result = await handler.execute(() => fetchUsersFromDB());
```
```

## Good Example

```typescript
// Checkout flow with explicit states
type CheckoutState =
  | { step: 'cart'; items: CartItem[] }
  | { step: 'shipping'; items: CartItem[]; address?: Address }
  | { step: 'payment'; items: CartItem[]; address: Address }
  | { step: 'confirming'; items: CartItem[]; address: Address; paymentMethod: PaymentMethod }
  | { step: 'success'; orderId: OrderId }
  | { step: 'error'; error: string };

// Each step has exactly the data it needs
// Transitions are explicit and validated
```

## Bad Example

```typescript
// ❌ Boolean flag soup
interface CheckoutState {
  items: CartItem[];
  address?: Address;
  paymentMethod?: PaymentMethod;
  orderId?: string;
  isLoading: boolean;
  isError: boolean;
  isSuccess: boolean;
  isInCart: boolean;
  isInShipping: boolean;
  isInPayment: boolean;
  isConfirming: boolean;
  error?: string;
}

// Problems:
// 1. Can isLoading and isError both be true?
// 2. Can multiple step flags be true?
// 3. When is address required vs optional?
// 4. Easy to forget to reset flags
```

## Anti-Patterns

1. **Multiple boolean flags**
   ```typescript
   // ❌
   const [isLoading, setIsLoading] = useState(false);
   const [isError, setIsError] = useState(false);
   const [isSuccess, setIsSuccess] = useState(false);
   ```

2. **String status with loose typing**
   ```typescript
   // ❌ - typos possible, no type narrowing
   const [status, setStatus] = useState('idle');
   if (status === 'laoding') { } // typo compiles!
   ```

3. **Optional fields that depend on state**
   ```typescript
   // ❌ - when is error defined?
   interface State {
     data?: Data;
     error?: Error;
     loading: boolean;
   }
   ```

## Exceptions

- **Very simple components**: A single `isOpen` for a modal is acceptable
- **External library constraints**: When a library enforces boolean patterns

## Checklist

- [ ] No multiple boolean flags for async state
- [ ] State uses discriminated union with `status` field
- [ ] Each state variant contains exactly required data
- [ ] Switch statements handle all cases
- [ ] TypeScript narrows types in each branch

## References

- Related: Pillar M (Saga) - saga states
- Template: `.claude/pillars/pillar-d/fsm-reducer.ts`
- Checklist: `.claude/pillars/pillar-d/checklist.md`

## Changelog

### Version 2.0.0 (2026-03-14)

**Issue**: #194 - Remove tech-stack dependencies

**Changes**:
- ✅ Added framework-agnostic core concepts section
- ✅ Created generic FSM implementation using TypeScript discriminated unions
- ✅ Replaced React-specific examples with multi-framework examples:
  - Example 1: React (useReducer)
  - Example 2: Vue 3 (ref)
  - Example 3: Svelte (writable stores)
  - Example 4: Node.js (class-based)
- ✅ All framework-specific code moved to clearly labeled "Implementation Examples" section

**Impact**:
- Core FSM pattern now applicable to ANY programming language
- Developers can see how to implement FSM in their framework of choice
- No vendor lock-in or framework coupling

**Backward compatibility**: Content reorganized but all original examples preserved
