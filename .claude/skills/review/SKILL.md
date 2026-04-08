---
name: review
description: |
  Conduct code review with quality checks, architecture validation, and framework compliance.
  TRIGGER when: user wants code reviewed ("review my code", "check this PR", "review these changes", "quality check").
  Dynamically detects project configuration (Pillars, architecture rules, ADRs) and adapts checks accordingly.
  DO NOT TRIGGER when: user wants to create/write code (not reviewing), or just wants explanations without quality assessment.
version: "2.4.1"
last-updated: "2026-03-30"
argument-hint: "[options]"
---

# Code Review - Quality and Architecture Validation

Automated code review that adapts to your project's configuration, checking quality, architecture, Pillars, ADRs, security, and performance.

## Overview

This skill provides comprehensive code review by:

**What it does:**
1. Runs quality gates (types, tests, linting)
2. Validates architecture patterns (dynamically detected)
3. **Checks skill version updates** (prevents version conflicts - Issue #401)
4. Checks Pillar compliance (based on project profile)
5. Verifies ADR compliance (scans docs/ADRs/)
6. Identifies security vulnerabilities
7. Detects performance issues
8. Writes review status for `/finish-issue` integration

**Why it's needed:**
Manual code review is time-consuming and inconsistent. This skill automates quality checks while adapting to each project's specific configuration.

**Key feature - Dynamic Detection:**
- No hardcoded assumptions
- Reads project profile to determine which Pillars to check
- Scans architecture rules from `.claude/rules/architecture/`
- Discovers ADRs from `docs/ADRs/`
- Different projects → different checks

**When to use:**
- After `/execute-plan` completes implementation
- Before `/finish-issue` creates PR
- Anytime you want code quality validation

## Arguments

```bash
/review [options]
```

**Common usage:**
```bash
/review                   # Review current branch changes
/review --strict          # Treat warnings as errors
/review --mode=auto       # Minimal output (for automation)
```

**Options:**
- `--strict` - Treat recommendations as blocking issues
- `--mode=auto` - Auto mode output (2 lines, used by /auto-solve-issue)
- `--files="pattern"` - Review specific files only

## Safety Features

This skill includes multiple safety mechanisms to ensure reliable and non-intrusive code review:

### 1. Read-Only Operations

**What it protects:**
- Never modifies source code or configuration files
- All checks are analysis-only (no writes to reviewed files)
- Safe to run multiple times without side effects

**How it works:**
```python
# All review operations use Read tool only
code_content = Read(file_path)  # ✅ Read-only
analyze_code(code_content)       # ✅ Analysis only

# Never uses Edit or Write on reviewed files
# ❌ Edit(file_path, ...) - NOT used in review
# ❌ Write(file_path, ...) - NOT used in review
```

**Benefits:**
- Can review any code safely (no risk of breaking changes)
- Idempotent - same review score every time
- No rollback needed if review fails

### 2. Dynamic Configuration Detection

**What it protects:**
- Avoids hardcoded assumptions about project structure
- Adapts to different tech stacks automatically
- No false positives from missing optional files

**How it works:**
```python
# Check if architecture rules exist before validating
if Path(".claude/rules/architecture/").exists():
    architecture_rules = load_architecture_rules()
    validate_against_rules(code, architecture_rules)
else:
    # Gracefully skip architecture checks
    log.info("No architecture rules found, skipping")

# Check if ADRs exist before compliance check
if Path("docs/ADRs/").exists():
    adrs = load_adrs()
    check_adr_compliance(code, adrs)
else:
    # Skip ADR checks if no ADRs defined
    log.info("No ADRs found, skipping ADR compliance")
```

**Benefits:**
- Works across different project profiles (tauri, nextjs, etc.)
- No configuration required
- Fails gracefully when optional components missing

### 3. Graceful Degradation

**What it protects:**
- Review continues even if some checks fail
- Missing configuration reduces scope but doesn't block
- Always produces a review score (even if limited)

**Degradation hierarchy:**
```
Full Review (all checks)
  ↓ Missing Pillars
Reduced Review (skip pillar checks)
  ↓ Missing ADRs
Basic Review (quality gates + architecture only)
  ↓ Missing architecture rules
Minimal Review (quality gates only)
  ↓ Never fails completely
Always produces score (even if 0/100)
```

**How it works:**
```python
score = 0
issues = []

# Quality gates (always run)
try:
    score += run_quality_gates()  # 30 points max
except Exception as e:
    log.error(f"Quality gates failed: {e}")
    issues.append({"severity": "error", "message": str(e)})

# Architecture (optional)
if has_architecture_rules():
    try:
        score += check_architecture()  # 25 points max
    except Exception as e:
        log.warning(f"Architecture check failed: {e}")
        # Continue without architecture points

# Pillars (optional)
if has_pillars():
    try:
        score += check_pillars()  # 20 points max
    except Exception as e:
        log.warning(f"Pillar check failed: {e}")

# Always write status file (even on partial failure)
write_status_file(score, issues)
```

**Benefits:**
- Review never completely fails
- Partial information better than no information
- Clear indication of what was checked vs skipped

### 4. Smart Strategy Selection

**What it protects:**
- Prevents expensive deep reviews on trivial changes
- Avoids shallow reviews on complex changes
- Optimizes cost vs coverage tradeoff

**How it works:**
```bash
# Analyze change size before selecting strategy
LINES_CHANGED=$(git diff --stat main...HEAD | tail -1 | grep -oE '[0-9]+ insertions')

if [ "$LINES_CHANGED" -lt 50 ]; then
  STRATEGY="SMALL"   # Focus on quality gates (fast)
elif [ "$LINES_CHANGED" -lt 200 ]; then
  STRATEGY="MEDIUM"  # Balanced review (standard)
else
  STRATEGY="LARGE"   # Deep review with full dimensions (thorough)
fi
```

**Strategy differences:**

| Strategy | Dimensions | Time | Use Case |
|----------|------------|------|----------|
| SMALL | Quality gates + quick architecture | ~30 sec | Doc updates, config changes |
| MEDIUM | All dimensions (standard weights) | ~2 min | Feature additions, bug fixes |
| LARGE | Deep architecture + full Pillars | ~5 min | Refactors, new modules |

**Benefits:**
- Fast reviews for simple changes
- Thorough reviews for complex changes
- Automatic optimization (no manual config)

### 5. Status File Validation

**What it protects:**
- Ensures status file is valid for /finish-issue integration
- Prevents stale status from affecting workflow
- Atomic writes prevent partial state

**How it works:**
```python
from datetime import datetime, timedelta

# Generate status with validity window
status = {
    "timestamp": datetime.now().isoformat(),
    "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat(),
    "score": total_score,
    # ... other fields
}

# Atomic write (no partial states)
import json, tempfile, shutil
temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
json.dump(status, temp_file, indent=2)
temp_file.close()
shutil.move(temp_file.name, ".claude/.review-status.json")
```

**Validation on read:**
```python
# /finish-issue checks validity before using
status = load_status_file()
if datetime.fromisoformat(status["valid_until"]) < datetime.now():
    # Status expired, run review again
    run_review()
else:
    # Status valid, skip re-review
    use_existing_status(status)
```

**Benefits:**
- 90-minute validity window balances freshness and efficiency
- Atomic writes prevent corruption
- Auto-expiration ensures reviews stay relevant

### Safety Best Practices

When using review:

1. **Trust the automation** - Review is designed to be safe; no need for --force
2. **Let it skip checks** - Missing config is normal; degradation is intentional
3. **Watch for patterns** - Repeated low scores indicate systematic issues
4. **Use in workflow** - Automated integration (/auto-solve-issue) is safest
5. **Review status files** - Check .review-status.json if behavior seems wrong

## AI Execution Instructions

**CRITICAL: Adaptive strategy and worktree support**

When executing `/review`, AI MUST follow this pattern:

### Step 0: Smart Decision (Adaptive Strategy)

**BEFORE running checks**, analyze changes and select strategy:

```bash
# Get change statistics
LINES_CHANGED=$(git diff --stat main...HEAD | tail -1 | grep -oE '[0-9]+ insertions' | cut -d' ' -f1)

if [ "$LINES_CHANGED" -lt 50 ]; then
  STRATEGY="SMALL"  # Focus on quality gates
elif [ "$LINES_CHANGED" -lt 200 ]; then
  STRATEGY="MEDIUM"  # Balanced review
else
  STRATEGY="LARGE"  # Deep review with full dimensions
fi
```

### Step 1: Create Todo List

```python
tasks = [
    TaskCreate("Smart decision - select strategy"),
    TaskCreate("Check goal coverage"),
    TaskCreate("Check skill version updates"),
    TaskCreate("Run quality gates"),
    TaskCreate("Check architecture patterns"),
    TaskCreate("Verify Pillar compliance"),
    TaskCreate("Check ADR compliance"),
    TaskCreate("Security scan"),
    TaskCreate("Performance check"),
    TaskCreate("Write review status file")
]
```

### Step 2: Check Goal Coverage (Phase 1)

**CRITICAL FIRST CHECK**: Verify implementation solves Issue requirements.

```bash
# Get issue number and load issue body
ISSUE_NUM=$(git branch --show-current | grep -oE '[0-9]+')
gh issue view $ISSUE_NUM --json body --jq '.body' > /tmp/issue-body.md

# Extract acceptance criteria
grep -E '- \[ \]|^- |^[0-9]+\.' /tmp/issue-body.md > /tmp/acceptance-criteria.txt

# Check if all criteria are addressed in code changes
# Score: requirements_coverage * 100
# If score < 80, auto-reject
```

**See**: [QUALITY.md](./QUALITY.md) for scoring details

### Step 3: Check Skill Version Updates

**Triggered when**: `.claude/skills/*/SKILL.md` files are modified.

```python
# AI-EXECUTABLE
import sys
from pathlib import Path
sys.path.insert(0, '.claude/skills/_scripts')

from utils.version import check_version_field, compare_versions

# Detect modified SKILL.md files
modified_skills = Bash("git diff --name-only HEAD | grep '.claude/skills/.*/SKILL.md'")

for skill_file in modified_skills.strip().split('\n'):
    if not skill_file:
        continue

    skill_path = Path(skill_file)

    # Check current version
    current_result = check_version_field(skill_path)

    # Get old version from git
    old_content = Bash(f"git show HEAD:{skill_file}")
    old_version = get_version_from_frontmatter(old_content)

    if current_result['has_version'] and old_version:
        if current_result['version'] == old_version:
            issues.append({
                "file": skill_file,
                "category": "version_unchanged",
                "severity": "warning",
                "message": f"Version not updated: {old_version}"
            })
```

**Shared module**: Uses `.claude/skills/_scripts/utils/version.py` (Issue #406)
**See**: [VERSION_CHECK.md](./VERSION_CHECK.md) for complete logic

### Step 4-9: Run Review Dimensions

Execute checks based on strategy selected in Step 0:

| Strategy | Dimensions | Focus |
|----------|------------|-------|
| SMALL | Quality gates, quick architecture | Fast validation |
| MEDIUM | All dimensions (standard weights) | Balanced |
| LARGE | Deep architecture, full Pillars | Comprehensive |

**Dimensions:**
1. **Quality Gates** (30 pts) - Types, tests, linting, build
2. **Architecture** (25 pts) - Layer separation, dependencies
3. **Pillars** (20 pts) - Error handling, logging, validation
4. **ADRs** (10 pts) - Compliance with decisions
5. **Security** (10 pts) - Vulnerabilities, input validation
6. **Performance** (5 pts) - Algorithm efficiency

**See**: [CHECKLIST.md](./CHECKLIST.md) for complete checklist

### Step 10: Write Status File

**CRITICAL**: Always write `.claude/.review-status.json`:

```python
import json
from datetime import datetime, timedelta

status = {
    "timestamp": datetime.now().isoformat(),
    "issue_number": issue_number,
    "status": "approved" if score > 90 else "needs_improvement" if score >= 70 else "rejected",
    "score": score,
    "breakdown": {
        "quality_gates": quality_score,
        "architecture": arch_score,
        "pillar_compliance": pillar_score,
        "adr_compliance": adr_score,
        "security": security_score,
        "performance": perf_score
    },
    "issues_count": {
        "blocking": len(blocking_issues),
        "recommendations": len(recommendations)
    },
    "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat()
}

with open(".claude/.review-status.json", "w") as f:
    json.dump(status, f, indent=2)
```

### Step 11: Output Results (Mode-Aware)

**Auto mode** (--mode=auto or called by /auto-solve-issue):
```text
✅ Review complete: 92/100 (approved)
Status: .claude/.review-status.json
```

**Interactive mode** (direct invocation):
```markdown
# Code Review: Issue #421

Score: 92/100 (approved)
Issues: 0 blocking, 2 recommendations

Top Recommendations:
1. Architecture - Move API call to service layer (-2 pts)
2. Performance - Use Set for faster lookup (-2 pts)

Full details: .claude/.review-status.json
Next: /finish-issue #421
```

## Workflow Steps

Copy this checklist to track progress:

```markdown
Task Progress:
- [ ] Step 0: Smart decision (adaptive strategy)
- [ ] Step 1: Create todo list
- [ ] Step 2: Check goal coverage
- [ ] Step 3: Check skill version updates
- [ ] Step 4: Run quality gates
- [ ] Step 5: Check architecture patterns
- [ ] Step 6: Verify Pillar compliance
- [ ] Step 7: Check ADR compliance
- [ ] Step 8: Security scan
- [ ] Step 9: Performance check
- [ ] Step 10: Write review status file
```

Execute these steps in sequence with TaskCreate/TaskUpdate for progress tracking.

## Review Dimensions

### 1. Quality Gates (30 points)

Basic quality checks:
- TypeScript compilation (types valid)
- Test execution (all passing)
- Linting (no errors)
- Build success

### 2. Architecture Validation (25 points)

Check architecture patterns:
- Layer separation (UI → Domain → Data)
- Dependency direction (inward only)
- Module boundaries (no circular deps)

### 3. Pillar Compliance (20 points)

Based on project profile:
- Error handling present
- Logging at appropriate levels
- Input validation at boundaries
- Documentation for public APIs
- Test coverage for changes

### 4. ADR Compliance (10 points)

Adherence to Architecture Decision Records:
- Scan `docs/ADRs/` directory
- Check code follows applicable ADRs
- Flag deviations with justification needed

### 5. Security (10 points)

Identify vulnerabilities:
- Input validation
- SQL injection prevention
- XSS prevention
- No secrets in code
- Dependency vulnerabilities

### 6. Performance (5 points)

Detect performance issues:
- Algorithmic complexity (avoid O(n²) where O(n) possible)
- Efficient data structures
- No memory leaks
- Database queries optimized

**See**: [QUALITY.md](./QUALITY.md) for scoring details

## Approval Levels

### ✅ Approved (Score > 90)
- All critical gates pass
- No blocking issues
- Ready to merge

### ⚠️ Needs Improvement (Score 70-90)
- Some gates fail or recommendations present
- No blocking issues
- Can merge with awareness

### ❌ Rejected (Score < 70)
- Critical gates fail
- Blocking issues present
- Must fix before merge

**See**: [QUALITY.md](./QUALITY.md) for threshold details

## Integration with /finish-issue

After review, `/finish-issue` reads the status file to skip re-review if valid (within 90 minutes).

**Workflow:**
```bash
/review              # Review code, write status
/finish-issue #N     # Reads status, skips re-review if valid
```

## Status File for Integration

After review, write `.claude/.review-status.json`:

```json
{
  "timestamp": "2026-03-30T14:30:00Z",
  "issue_number": 421,
  "status": "approved",
  "score": 92,
  "breakdown": {
    "quality_gates": 30,
    "architecture": 23,
    "pillar_compliance": 18,
    "adr_compliance": 10,
    "security": 10,
    "performance": 1
  },
  "issues_count": {
    "blocking": 0,
    "recommendations": 2
  },
  "valid_until": "2026-03-30T16:00:00Z"
}
```

**Status values:**
- `"approved"` - Score > 90, no blocking issues
- `"needs_improvement"` - Score 70-90, minor issues
- `"rejected"` - Score < 70, must fix before proceeding

**Validity:** 90 minutes from review completion

**Used by:**
- `/auto-solve-issue` - Checkpoint 2 logic (auto-continue if score ≥ 90)
- `/finish-issue` - Skips re-review if status valid

## Usage Examples

### Example 1: Review Current Changes

**User says:**
> "review my code"

**What happens:**
1. Detect issue number from branch
2. Run smart decision (analyze change size)
3. Execute adaptive review strategy
4. Generate report with score
5. Write status file

**See**: [EXAMPLES.md](./EXAMPLES.md) for more examples

### Example 2: Goal Coverage Failure

**Scenario:** Issue requires 5 acceptance criteria, only 3 implemented.

**Output:**
```markdown
## 1. Goal Coverage Check ❌

**Issue Requirements**: 3/5 (60%) ← Below 80% threshold
Missing: AC3, AC5

**Status**: REJECTED (blocking)
```

### Example 3: Skill Version Not Updated

**Scenario:** Modified SKILL.md but forgot version bump.

**Output:**
```markdown
## 3. Skill Version Check ⚠️

⚠️ `.claude/skills/eval-plan/SKILL.md`
   Version: 1.1.0 (unchanged)
   Suggested: 1.2.0 (minor bump)

**Status**: NEEDS_IMPROVEMENT (blocking)
```

**See**: [VERSION_CHECK.md](./VERSION_CHECK.md) for details

## Best Practices

1. **Run before /finish-issue** - Catches issues early
2. **Trust dynamic detection** - Skill adapts to your project
3. **Fix blocking issues** - Don't merge with critical failures
4. **Learn from reviews** - Improves code quality over time
5. **Re-review after fixes** - Status expires in 90 minutes

## Error Handling

This skill implements comprehensive error handling to ensure robust operation across different scenarios:

### Configuration Errors

**Missing architecture rules:**
```python
# Error: .claude/rules/architecture/ directory not found
# Recovery: Skip architecture validation dimension

try:
    arch_rules = load_architecture_rules(".claude/rules/architecture/")
    score += validate_architecture(code, arch_rules, max_points=25)
except FileNotFoundError:
    log.info("Architecture rules not found, skipping architecture checks")
    # Continue without architecture points (graceful degradation)
```

**Invalid status file format:**
```python
# Error: .claude/.review-status.json is corrupted or wrong format
# Recovery: Regenerate status file

try:
    status = json.load(open(".claude/.review-status.json"))
    validate_status_schema(status)
except (JSONDecodeError, ValidationError) as e:
    log.warning(f"Invalid status file: {e}, regenerating")
    os.remove(".claude/.review-status.json")
    # Run fresh review to generate valid status
```

**Read permission denied:**
```python
# Error: Cannot read files due to permission issues
# Recovery: Show clear error with resolution steps

try:
    content = Read(file_path)
except PermissionError:
    print(f"""
❌ Error: Cannot read file due to permissions

File: {file_path}
Cause: Permission denied

Fix:
1. Check file permissions: ls -la {file_path}
2. Grant read access: chmod +r {file_path}
3. Check directory permissions: chmod +rx $(dirname {file_path})
""")
    raise ReviewError("Permission denied")
```

### GitHub API Errors

**Rate limit exceeded:**
```python
# Error: GitHub API rate limit hit
# Recovery: Retry with exponential backoff

import time

def fetch_issue_with_retry(issue_num, max_retries=3):
    for attempt in range(max_retries):
        try:
            return gh_issue_view(issue_num)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                log.warning(f"Rate limit hit, retry in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                # Max retries exceeded
                print("""
⚠️ GitHub API rate limit exceeded

Tried: {max_retries} attempts with backoff
Action: Wait 60 minutes or use --skip-goal-coverage

Check limit: gh api rate_limit
""")
                raise
```

**Authentication failed:**
```python
# Error: gh CLI not authenticated
# Recovery: Guide user to authenticate

try:
    gh_auth_status()
except AuthenticationError:
    print("""
❌ Error: GitHub CLI not authenticated

Required for: Fetching issue body to check acceptance criteria

Fix: gh auth login

Follow prompts to authenticate via browser or token
""")
    raise ReviewError("Authentication required")
```

**Issue not found:**
```python
# Error: Issue number doesn't exist
# Recovery: Validate issue number and suggest alternatives

try:
    issue = gh_issue_view(issue_num)
except IssueNotFoundError:
    # Check if issue exists in different repo
    current_repo = gh_repo_view()

    print(f"""
❌ Error: Issue #{issue_num} not found

Repository: {current_repo}

Check:
1. Issue number correct? View issues: gh issue list
2. Issue in different repo? Switch repo: cd /path/to/repo
3. Issue was deleted? Check closed issues: gh issue list --state closed

Fix: Provide correct issue number or use --skip-goal-coverage
""")
    raise ReviewError(f"Issue #{issue_num} not found")
```

### File System Errors

**Cannot write status file:**
```python
# Error: Cannot write .claude/.review-status.json
# Recovery: Warn but continue (status file is optional for interactive mode)

try:
    with open(".claude/.review-status.json", "w") as f:
        json.dump(status, f, indent=2)
except (PermissionError, IOError) as e:
    log.warning(f"Cannot write status file: {e}")

    if is_auto_mode:
        # Auto mode needs status file (blocking)
        print(f"""
❌ Error: Cannot write status file

Path: .claude/.review-status.json
Cause: {e}

Fix:
1. Check directory permissions: chmod 755 .claude/
2. Check disk space: df -h
3. Remove existing file: rm .claude/.review-status.json
""")
        raise ReviewError("Status file write failed")
    else:
        # Interactive mode can continue without status file (non-blocking)
        print(f"""
⚠️ Warning: Cannot write status file (non-blocking)

Review score: {status['score']}/100
Status file: {e}

Continuing with interactive output...
""")
        # Continue without status file
```

**Worktree path not found:**
```python
# Error: Plan references non-existent worktree
# Recovery: Fallback to main repository

worktree_path = extract_worktree_from_plan(plan_content)

if worktree_path and not Path(worktree_path).exists():
    log.warning(f"Worktree not found: {worktree_path}, falling back to main repo")
    worktree_path = None  # Use current directory instead

# Use fallback path
file_path = f"{worktree_path or '.'}/src/component.tsx"
```

**Plan file missing:**
```python
# Error: .claude/plans/active/issue-N-plan.md not found
# Recovery: Skip goal coverage check (use 0 points)

try:
    plan_content = Read(plan_file)
    goal_coverage_score = check_goal_coverage(plan_content, issue)
except FileNotFoundError:
    log.info(f"Plan file not found: {plan_file}, skipping goal coverage")
    goal_coverage_score = 0  # No points for goal coverage

    # Add note to review output
    issues.append({
        "severity": "info",
        "message": "Plan file not found - goal coverage check skipped"
    })
```

### Scoring Calculation Errors

**Division by zero in percentage calculation:**
```python
# Error: Empty dimensions cause division by zero
# Recovery: Handle edge cases with defaults

def calculate_percentage(completed, total):
    if total == 0:
        return 100 if completed == 0 else 0  # Empty set is 100% complete
    return (completed / total) * 100

# Example: No acceptance criteria to check
criteria_coverage = calculate_percentage(met_criteria, total_criteria)
```

**Invalid score values:**
```python
# Error: Dimension score exceeds maximum
# Recovery: Clamp to valid range [0, max]

def validate_score(score, max_score):
    if score < 0:
        log.warning(f"Negative score {score}, clamping to 0")
        return 0
    if score > max_score:
        log.warning(f"Score {score} exceeds max {max_score}, clamping")
        return max_score
    return score

architecture_score = validate_score(raw_score, max_points=25)
```

### Recovery Mechanisms

**Auto-retry with exponential backoff:**
```python
# 3 attempts with increasing wait times
def retry_with_backoff(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except TransientError as e:
            if attempt < max_attempts - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                log.warning(f"Attempt {attempt + 1} failed, retry in {wait}s")
                time.sleep(wait)
            else:
                raise  # Max attempts exceeded
```

**Fallback to basic checks:**
```python
# If advanced checks fail, fall back to minimal viable review
def review_with_fallback(code):
    score = 0

    # Always try quality gates (critical)
    score += run_quality_gates(code)  # May raise if tests fail

    # Try advanced checks (optional)
    try:
        score += check_architecture(code)
        score += check_pillars(code)
        score += check_adrs(code)
    except Exception as e:
        log.warning(f"Advanced checks failed: {e}, using basic review")
        # Continue with basic review score

    return score
```

**Clear error messages with resolution steps:**
```python
# Every error includes:
# 1. What went wrong
# 2. Why it matters
# 3. How to fix it
# 4. What happens next

print(f"""
❌ Error: {error_type}

What: {description}
Cause: {root_cause}

Fix:
1. {step_1}
2. {step_2}
3. {step_3}

Alternative: {fallback_option}
""")
```

### Error Handling Best Practices

When errors occur during review:

1. **Read error messages** - They include resolution steps
2. **Check permissions** - Most file errors are permission-related
3. **Verify authentication** - gh CLI must be logged in for issue fetching
4. **Use fallbacks** - --skip-goal-coverage disables issue fetching
5. **Re-run review** - After fixing errors, status files auto-regenerate

## Worktree Support

If the issue was started with `/start-issue` and a worktree was created, review operations MUST use the worktree path.

### Auto-Detection

```bash
PLAN_FILE=".claude/plans/active/issue-${ISSUE_NUM}-plan.md"
WORKTREE_PATH=$(grep "^**Worktree**:" "$PLAN_FILE" | cut -d' ' -f2)
```

### File Operations

**All file reads must use absolute worktree paths**:

```bash
# ✅ CORRECT - Review files in worktree
Read ${WORKTREE_PATH}/src/components/Button.tsx
git -C ${WORKTREE_PATH} diff main...HEAD

# ❌ WRONG - Reviews main repo instead
Read src/components/Button.tsx
git diff main...HEAD
```

## Task Management

After each step completion, update progress using TaskUpdate:

```python
# Mark task in progress
TaskUpdate(task_id, status="in_progress")

# Execute review dimension
execute_dimension()

# Mark complete
TaskUpdate(task_id, status="completed")
```

## Final Verification

Before completing review, verify:

```markdown
- [ ] All review tasks completed
- [ ] Status file written (.claude/.review-status.json)
- [ ] Approval level determined (✅/⚠️/❌)
- [ ] All blocking issues documented
- [ ] Score calculated (0-100)
- [ ] Valid until timestamp set (90 min)
```

## Related Skills

- **/eval-plan** - Validates plans (Phase 1.5 - symmetric validation for planning)
- **/auto-solve-issue** - Calls this skill in Phase 2.5 (quality check after implementation)
- **/finish-issue** - Uses review status to skip re-review
- **/execute-plan** - Implementation phase (run before this)

## Documentation

- **[CHECKLIST.md](./CHECKLIST.md)** - Complete review checklist for all dimensions
- **[QUALITY.md](./QUALITY.md)** - Scoring methodology and approval thresholds
- **[VERSION_CHECK.md](./VERSION_CHECK.md)** - Skill version validation logic (Issue #401)
- **[EXAMPLES.md](./EXAMPLES.md)** - Real-world usage examples

---

**Version:** 2.4.1
**Last Updated:** 2026-03-30
**Pattern:** Tool-Reference (guides review process)
**Compliance:** ADR-001 ✅ | ADR-014 ✅ | WORKFLOW_PATTERNS.md ✅
**Changelog:**
- v2.4.1: Use shared version.py module for version checking (Issue #406)
- v2.4.0: Split into 5 documents for ADR-014 compliance (Issue #421)
- v2.3.0: Added skill version check to prevent version conflicts (Issue #401)
- v2.2.0: Added mode-aware output (2 lines auto, ≤20 lines interactive)
- v2.1.0: Dynamic configuration detection
- v2.0.0: Added Pillar and ADR compliance checks
