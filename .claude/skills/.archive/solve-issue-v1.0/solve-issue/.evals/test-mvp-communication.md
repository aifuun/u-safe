# Test: MVP Communication (Python ↔ AI)

**Goal**: Verify Python coordinator can communicate with AI executor through JSON instruction files.

## Test Setup

**Prerequisites:**
- coordinator.py exists
- instruction_manager.py exists
- solve-issue SKILL.md exists
- Python 3.8+ installed

## Test Case 1: Write and Read Instructions

**Test:** coordinator.py writes instruction → AI reads instruction

**Steps:**
1. Run coordinator manually:
   ```bash
   cd .claude/skills/solve-issue/scripts
   python3 coordinator.py 999 auto  # Test issue #999
   ```

2. Check instructions file created:
   ```bash
   cat .claude/skills/solve-issue/.temp/instructions.json
   ```

3. Expected output (Phase 1 instruction):
   ```json
   {
     "timestamp": "2026-03-18T...",
     "issue_number": 999,
     "instruction": {
       "type": "call_skill",
       "phase": "1",
       "skill_name": "start-issue",
       "skill_args": "999",
       "message": "Executing /start-issue 999"
     }
   }
   ```

**Pass criteria:**
- ✅ File created at correct path
- ✅ JSON format valid
- ✅ Contains correct instruction type, phase, skill_name

## Test Case 2: Write Completion Marker

**Test:** AI writes completion → coordinator reads completion

**Steps:**
1. Manually create completion file:
   ```bash
   cat > .claude/skills/solve-issue/.temp/completions.json << 'EOF'
   {
     "phase": "1",
     "status": "success",
     "timestamp": 1710000000
   }
   EOF
   ```

2. Coordinator should detect completion and proceed to Phase 1.5

**Pass criteria:**
- ✅ Coordinator reads completion file
- ✅ Coordinator deletes completion file after reading
- ✅ Coordinator proceeds to next phase

## Test Case 3: File Locking

**Test:** No race conditions when reading/writing simultaneously

**Steps:**
1. Run coordinator in background:
   ```bash
   python3 coordinator.py 999 auto &
   COORDINATOR_PID=$!
   ```

2. Simultaneously try to read instructions (simulate AI):
   ```python
   import json
   from instruction_manager import InstructionManager
   from pathlib import Path

   manager = InstructionManager(Path(".claude/skills/solve-issue/.temp"))
   instruction = manager.read_instruction()
   print(instruction)
   ```

3. No errors should occur (file lock prevents corruption)

**Pass criteria:**
- ✅ No file corruption
- ✅ No JSON parse errors
- ✅ Either read succeeds or waits for lock

## Test Case 4: Timeout Handling

**Test:** Coordinator times out if AI doesn't respond

**Steps:**
1. Run coordinator (don't write completion):
   ```bash
   timeout 10 python3 coordinator.py 999 auto
   ```

2. Expected: Coordinator waits, then times out after default timeout (300s)
   - For testing, modify timeout to 10s in coordinator.py

**Pass criteria:**
- ✅ Coordinator waits for completion
- ✅ Coordinator raises TimeoutError after timeout
- ✅ Error message is clear

## Test Case 5: Error Propagation

**Test:** Coordinator writes error instruction when exception occurs

**Steps:**
1. Modify coordinator to simulate error (e.g., invalid skill name)

2. Check error instruction written:
   ```json
   {
     "instruction": {
       "type": "error",
       "phase": "1",
       "message": "..."
     }
   }
   ```

**Pass criteria:**
- ✅ Error instruction written
- ✅ Coordinator exits gracefully
- ✅ AI can read and display error

## Integration Test: Single Phase Execution

**Test:** Full cycle - coordinator → AI → completion → next phase

**Steps:**
1. Start coordinator (will write instruction for Phase 1)
2. AI reads instruction manually:
   ```bash
   # Simulate AI reading
   python3 -c "
   import json
   with open('.claude/skills/solve-issue/.temp/instructions.json') as f:
       data = json.load(f)
       print(f'Read: {data}')
   "
   ```
3. AI calls skill (simulated):
   ```bash
   echo "Simulating /start-issue 999"
   ```
4. AI writes completion:
   ```bash
   cat > .claude/skills/solve-issue/.temp/completions.json << 'EOF'
   {"phase": "1", "status": "success", "timestamp": 1710000000}
   EOF
   ```
5. Coordinator reads completion, proceeds to Phase 1.5

**Pass criteria:**
- ✅ Full cycle completes
- ✅ Coordinator proceeds to Phase 1.5
- ✅ No errors or hangs

## Acceptance Criteria

**MVP communication mechanism passes if:**
- [ ] All 6 test cases pass
- [ ] No file corruption
- [ ] No race conditions
- [ ] Error handling works
- [ ] Timeout mechanism works
- [ ] Full single-phase cycle works

## Next Steps After MVP Tests Pass

1. Run full workflow test (all 5 phases)
2. Add Phase 2-3 features (error handling, logging, state management)
3. Add advanced features (batch mode, resume, progress visibility)

## Notes

**Test environment:**
- Run tests in worktree: `/Users/woo/dev/ai-dev-253-create-solve-issue-skill`
- Use test issue #999 (non-existent) to avoid polluting real issues
- Clean up temp files after tests: `rm .claude/skills/solve-issue/.temp/*`

**Common issues:**
- File not found: Check paths are relative to repo root
- JSON parse error: Check file locking is working
- Timeout: Adjust timeout value for testing (default 300s is too long)
