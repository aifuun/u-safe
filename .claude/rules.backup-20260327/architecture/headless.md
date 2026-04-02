---
paths: "**/headless/*.ts"
---
# Headless Hook Rules

> 📖 **Complete Guide**: `.prot/pillars/q3-structure-boundaries/pillar-l/headless.md`

## Quick Check (30 seconds)
- [ ] Returns `{ state, ...actions }` pattern, never JSX
- [ ] State uses FSM union types (`'idle' | 'loading' | 'success' | 'error'`)
- [ ] No DOM manipulation or `window`/`document` access
- [ ] Calls adapters for I/O (not direct `fetch`)
- [ ] Uses `useReducer` for complex state (not multiple `useState`)
- [ ] All actions wrapped in `useCallback`
- [ ] Can be tested without React Testing Library

## Core Pattern
```typescript
// Standard headless hook - copy directly
type State = { status: 'idle' | 'loading' | 'success' | 'error'; data?: User };

function useUserLogic(userId: UserId) {
  const [state, setState] = useState<State>({ status: 'idle' });

  const load = useCallback(async () => {
    setState({ status: 'loading' });
    try {
      const data = await userApi.fetchUser(userId);
      setState({ status: 'success', data });
    } catch {
      setState({ status: 'error' });
    }
  }, [userId]);

  return { state, load };  // Data + actions, no JSX
}
```

## When to Read Full Pillar?
- ❓ Need complete FSM state machine examples → Read Pillar L
- ❓ Unsure how to handle complex multi-step state → Read Pillar L
- ❓ Need anti-patterns and common mistakes → Read Pillar L
- ❓ Want comprehensive testing strategies → Read Pillar L

## Related
- **Pillar L**: `.prot/pillars/q3-structure-boundaries/pillar-l/headless.md` (complete theory)
- **Pillar D**: FSM (Finite State Machines)
- **Pillar K**: Testing (test pyramid)
- **Rule**: `stores.md` (Zustand vanilla stores)
- **Rule**: `views.md` (View layer that consumes headless hooks)
