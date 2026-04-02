# Post-Code Checklist

> Run AFTER all tasks complete, before issue close
>
> **Full Details**: See [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md#quick-lookup-checklist-by-phase) for complete checklists.

## Essential Post-Code Audits

### 1. Data Integrity (Q1)

#### Pillar A: Nominal Typing
- [ ] No primitive types for domain entities in codebase
- [ ] All ID parameters use branded types
- [ ] Type system catches ID type mismatches (verified)

→ **Full checklist**: [Pillar A: Nominal Typing](../pillars/q1-data-integrity/pillar-a/nominal-typing.md)

#### Pillar B: Airlock (Schema Validation)
- [ ] All external data validated with schemas
- [ ] No `any` types from external sources
- [ ] Schema tests verify validation logic

→ **Full checklist**: [Pillar B: Airlock](../pillars/q1-data-integrity/pillar-b/airlock.md)

#### Pillar C: Mocking
- [ ] All tests use factories, not inline object literals
- [ ] No magic strings in tests
- [ ] Mock data is realistic and diverse

→ **Full checklist**: [Pillar C: Mocking](../pillars/q1-data-integrity/pillar-c/mocking.md)

#### Pillar D: FSM
- [ ] No boolean flags for state
- [ ] State transitions testable and predictable
- [ ] State machine documented

→ **Full checklist**: [Pillar D: FSM](../pillars/q1-data-integrity/pillar-d/fsm.md)

---

### 2. Flow & Concurrency (Q2)

#### Pillar E: Adaptive Orchestration
- [ ] Task tier documented in PR description
- [ ] Pattern matches tier classification
- [ ] No over-engineering or under-engineering

→ **Full checklist**: [Pillar E: Orchestration](../pillars/q2-flow-concurrency/pillar-e/orchestration.md)

---

### 3. Structure & Boundaries (Q3)

#### Pillar I: Firewalls
- [ ] No circular dependencies
- [ ] Layer boundaries respected (verified with tooling)
- [ ] Dependency direction correct (outer → inner)

→ **Full checklist**: [Pillar I: Firewalls](../pillars/q3-structure-boundaries/pillar-i/firewalls.md)

#### Pillar K: Testing
- [ ] Coverage ≥70% overall (≥80% for critical paths)
- [ ] Fast unit tests (<1s total for unit tests)
- [ ] E2E tests stable and minimal

→ **Full checklist**: [Pillar K: Testing](../pillars/q3-structure-boundaries/pillar-k/testing.md)

#### Pillar L: Headless
- [ ] No UI code in headless hooks/modules
- [ ] All hooks unit tested (without UI framework)
- [ ] View components thin and declarative

→ **Full checklist**: [Pillar L: Headless](../pillars/q3-structure-boundaries/pillar-l/headless.md)

---

### 4. Resilience & Observability (Q4)

#### Pillar R: Observability
- [ ] Logs queryable by semantic fields
- [ ] All errors logged with context (traceId, userId, etc.)
- [ ] No debug statements in production code

→ **Full checklist**: [Pillar R: Observability](../pillars/q4-resilience-observability/pillar-r/observability.md)

---

## T3-Specific Verification

If Tier 3 (Saga/Complex operations) was implemented:

#### Pillar Q: Idempotency
- [ ] Critical operations are idempotent
- [ ] Retry tests confirm same result
- [ ] Idempotency cache has appropriate TTL

→ **Full checklist**: [Pillar Q: Idempotency](../pillars/q2-flow-concurrency/pillar-q/idempotency.md)

#### Pillar F: Concurrency
- [ ] All concurrent writes use version checking
- [ ] Conflict scenarios tested
- [ ] Race condition prevention verified

→ **Full checklist**: [Pillar F: Concurrency](../pillars/q2-flow-concurrency/pillar-f/concurrency.md)

#### Pillar M: Saga
- [ ] All multi-service operations use saga pattern
- [ ] Failure scenarios tested with compensation
- [ ] Saga resumable after partial failure

→ **Full checklist**: [Pillar M: Saga](../pillars/q4-resilience-observability/pillar-m/saga.md)

#### Pillar N: Context
- [ ] All operations traceable via traceId
- [ ] Logs can be filtered by traceId
- [ ] Cross-service tracing works (if applicable)

→ **Full checklist**: [Pillar N: Context](../pillars/q4-resilience-observability/pillar-n/context.md)

---

## Security Quick Check

- [ ] No secrets in code (API keys, passwords, tokens)
- [ ] Input validated at all boundaries (Pillar B)
- [ ] No injection vulnerabilities (SQL, command, XSS, etc.)
- [ ] Authorization checks present (Pillar H)

---

## Final Verdict

```
□ PASS - Ready for PR and merge
□ NEEDS_FIX - Create fix tasks before merge
```

---

## Test Coverage Summary

| Layer | Minimum Required | Actual |
|-------|------------------|--------|
| Domain Logic | 100% | ___% |
| Headless | High (≥80%) | ___% |
| Adapters | Contract tests | ___% |
| Sagas (T3) | Integration | ___% |
| **Overall** | **≥70%** | ___% |

---

## Git Workflow Cleanup

**After PR is merged to main/development:**

- [ ] **Delete feature branch** (local and remote)
  ```bash
  # Switch to main and pull merged changes
  git checkout main
  git pull origin main

  # Delete local feature branch
  git branch -d feature/<issue>-<description>

  # Delete remote feature branch (if not auto-deleted)
  git push origin --delete feature/<issue>-<description>

  # Clean up other merged branches
  git branch -v | grep "\[gone\]" | awk '{print $1}' | xargs git branch -d
  ```

- [ ] **Verify issue is closed** (if using "Closes #N" in PR)
  ```bash
  gh issue view <issue-number>  # Should show "Status: Closed"
  ```

- [ ] **Archive plan file** (if feature had a plan)
  ```bash
  # Move from active to archive
  mv .claude/plans/active/#<n>-*.md .claude/plans/archive/
  git add .claude/plans/
  git commit -m "chore: archive issue #<n> plan"
  git push origin main
  ```

---

## Related Resources

- **Complete Checklists**: [PILLAR_CHECKLISTS.md](./PILLAR_CHECKLISTS.md) - All 18 Pillars with full details
- **Previous Phase**: [in-code.md](./in-code.md) - Implementation checklist
- **Planning Phase**: [pre-code.md](./pre-code.md) - Pre-implementation checklist
