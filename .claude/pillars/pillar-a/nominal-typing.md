# Pillar A: Absolute Nominal Typing

> Eliminate "Primitive Obsession" bugs through branded types

## Rule

The use of primitive types (`string`, `number`, `boolean`) to represent Domain Entities or Identifiers is **STRICTLY FORBIDDEN**.

## Purpose

Prevent bugs where values are accidentally swapped:
- Passing `UserId` where `OrderId` is expected
- Confusing `price` with `quantity`
- Mixing `email` with `name`

TypeScript's structural typing treats all strings as the same type. Nominal typing creates distinct types.

## Implementation (TypeScript)

### Branded Types

```typescript
// Define branded types for each ID
type UserId = string & { readonly __brand: unique symbol };
type OrderId = string & { readonly __brand: unique symbol };
type ProductId = string & { readonly __brand: unique symbol };

// Now these are incompatible:
declare function getUser(id: UserId): User;
declare function getOrder(id: OrderId): Order;

const userId = 'u_123' as UserId;
const orderId = 'o_456' as OrderId;

getUser(userId);   // ✅ OK
getUser(orderId);  // ❌ Type error!
```

### Value Objects for Complex Types

```typescript
// For values with validation logic
class Email {
  private readonly value: string;
  private readonly __brand!: 'Email';

  private constructor(value: string) {
    this.value = value;
  }

  static create(raw: string): Email {
    if (!raw.includes('@')) {
      throw new Error('Invalid email');
    }
    return new Email(raw);
  }

  toString(): string {
    return this.value;
  }
}
```

### Type Conversion at Boundaries

```typescript
// At API/URL boundary - validate and convert
function toUserId(raw: string): UserId {
  if (!raw || !raw.startsWith('u_')) {
    throw new Error('Invalid user ID format');
  }
  return raw as UserId;
}

// In route handler
app.get('/users/:id', (req) => {
  const userId = toUserId(req.params.id);  // Convert at boundary
  return userService.getUser(userId);
});
```

## Immutability with Nominal Types

Combining nominal typing with immutability creates bulletproof data integrity.

### Immutable Branded Types

```typescript
// Immutable nominal types - cannot be accidentally modified
type UserId = Readonly<string & { readonly __brand: 'UserId' }>;
type Email = Readonly<string & { readonly __brand: 'Email' }>;

type User = Readonly<{
  id: UserId;
  name: string;
  email: Email;
  createdAt: Date;
}>;

// Attempting to modify triggers compile error
const user: User = createUser();
user.name = 'New Name';  // ❌ Error: Cannot assign to 'name' because it is a read-only property
```

### Functional Updates

Use the spread operator to create new objects instead of mutating:

```typescript
// Functional update pattern
function updateUserName(user: User, newName: string): User {
  return Object.freeze({
    ...user,
    name: newName
  });
}

// Functional update with validation
function updateUserEmail(user: User, newEmail: string): User {
  const validatedEmail = Email.create(newEmail);
  return Object.freeze({
    ...user,
    email: validatedEmail
  });
}

// Nested immutable updates
type Order = Readonly<{
  id: OrderId;
  user: User;
  items: readonly OrderItem[];
}>;

function updateOrderUserEmail(order: Order, newEmail: Email): Order {
  return Object.freeze({
    ...order,
    user: updateUserEmail(order.user, newEmail)
  });
}
```

### Immutable Collections

```typescript
// Use readonly arrays for collections
type ShoppingCart = Readonly<{
  id: CartId;
  items: readonly CartItem[];
  total: Money;
}>;

// Functional collection updates
function addItem(cart: ShoppingCart, item: CartItem): ShoppingCart {
  return Object.freeze({
    ...cart,
    items: [...cart.items, item],
    total: calculateTotal([...cart.items, item])
  });
}

function removeItem(cart: ShoppingCart, itemId: ItemId): ShoppingCart {
  return Object.freeze({
    ...cart,
    items: cart.items.filter(item => item.id !== itemId),
    total: calculateTotal(cart.items.filter(item => item.id !== itemId))
  });
}

// Immutable map operations
function updateItemQuantity(
  cart: ShoppingCart,
  itemId: ItemId,
  newQuantity: number
): ShoppingCart {
  return Object.freeze({
    ...cart,
    items: cart.items.map(item =>
      item.id === itemId
        ? Object.freeze({ ...item, quantity: newQuantity })
        : item
    ),
    total: calculateTotal(
      cart.items.map(item =>
        item.id === itemId ? { ...item, quantity: newQuantity } : item
      )
    )
  });
}
```

### When to Use Immutability

**✅ Use immutability when:**
- Representing domain entities (User, Order, Product)
- Passing data between layers (API → Service → Domain)
- State management (Redux, Zustand, React state)
- Concurrent operations (prevents race conditions)
- Audit trails (preserve historical states)

**⚠️ Consider mutability when:**
- Performance-critical tight loops (with benchmarking proof)
- Large datasets that copy costs are prohibitive
- Internal implementation details (not exposed to API)
- Builder patterns for complex object construction

### Immutability Anti-Patterns

```typescript
// ❌ BAD - Mutable nominal types
type UserId = string & { readonly __brand: 'UserId' };
type User = {  // Missing Readonly
  id: UserId;
  name: string;
};

const user: User = createUser();
user.name = 'Hacker';  // ✅ Compiles! ❌ Data corruption risk

// ❌ BAD - Mutating instead of returning new object
function updateUser(user: User, name: string): void {
  user.name = name;  // Mutation!
}

// ❌ BAD - Shallow freeze only
const user = Object.freeze({
  id: userId,
  address: { street: '123 Main' }  // address is still mutable!
});
user.address.street = 'Hacked';  // ✅ Works! ❌ Mutation leaked

// ✅ GOOD - Deep immutability
type Address = Readonly<{
  street: string;
  city: string;
}>;

type User = Readonly<{
  id: UserId;
  address: Address;  // Nested readonly
}>;
```

## Good Example

```typescript
// Domain types
type CartId = string & { readonly __brand: unique symbol };
type ItemId = string & { readonly __brand: unique symbol };
type Money = number & { readonly __brand: unique symbol };

interface CartItem {
  id: ItemId;
  price: Money;
  quantity: number;
}

interface Cart {
  id: CartId;
  items: CartItem[];
}

// Functions are type-safe
function addToCart(cartId: CartId, itemId: ItemId): void {
  // Cannot accidentally swap cartId and itemId
}

// Type conversion at boundary
function toMoney(cents: number): Money {
  if (cents < 0) throw new Error('Money cannot be negative');
  return cents as Money;
}
```

## Bad Example

```typescript
// ❌ Primitive obsession
interface Cart {
  id: string;        // Which string? Cart? User? Order?
  items: {
    id: string;      // Item ID? Product ID?
    price: number;   // Dollars? Cents? Could be quantity!
    quantity: number;
  }[];
}

function addToCart(cartId: string, itemId: string): void {
  // Easy to swap arguments - no compiler help
}

// Accident waiting to happen:
addToCart(itemId, cartId);  // ✅ Compiles! ❌ Runtime bug!
```

## Anti-Patterns

1. **Raw string IDs everywhere**
   ```typescript
   // ❌ BAD
   const userId: string = 'u_123';
   ```

2. **Direct casting without validation**
   ```typescript
   // ❌ BAD - no validation
   const userId = rawInput as UserId;
   ```

3. **Using primitives in function signatures**
   ```typescript
   // ❌ BAD
   function processOrder(userId: string, orderId: string, amount: number)
   ```

## Exceptions

- **View Layer Boundary**: Primitives are allowed at the very edge (URL params, form inputs) immediately before conversion to Domain types
- **Third-party APIs**: When interfacing with external APIs that use strings, convert at the adapter layer

## Checklist

- [ ] All entity IDs use branded types
- [ ] No `string` type for domain identifiers
- [ ] No `number` type for money/amounts
- [ ] Conversion functions exist at boundaries
- [ ] Conversion functions include validation
- [ ] Types are immutable by default (`Readonly<T>`)
- [ ] Updates return new objects (no mutations)
- [ ] Collections use immutable data structures (`readonly T[]`)

## References

- Related: Pillar B (Airlock) - validation at boundaries
- Template: `.claude/pillars/pillar-a/branded.ts`
- Checklist: `.claude/pillars/pillar-a/checklist.md`
- Audit: `.claude/pillars/pillar-a/audit.ts`

## Changelog

### Version 2.1.0 (2026-03-14)

**Issue**: #195 - Phase 2: Integrate missing best practices

**Changes**:
- ✅ Added comprehensive "Immutability with Nominal Types" section
- ✅ Covered `Readonly<T>` and `Object.freeze()` patterns
- ✅ Demonstrated functional update patterns
- ✅ Added immutable collections examples
- ✅ Showed when to use vs when to avoid immutability
- ✅ Added immutability checklist items
- ✅ Added immutability anti-patterns

**Impact**:
- Immutability best practice now covered (Data Integrity category)
- Developers have clear patterns for preventing accidental mutations
- Combines nominal typing with immutability for maximum type safety

**Backward compatibility**: All existing content preserved, purely additive change
