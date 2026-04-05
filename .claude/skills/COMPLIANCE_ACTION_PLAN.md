# Skills Compliance Action Plan

**Generated**: 2026-03-11
**Audit Score**: 92.5/100 average
**Status**: 16 passed, 3 need improvement, 1 failed

---

## 🚨 Priority 0 - Critical (修复时间: 2-3 小时)

### 1. skill-creator (39/100) ❌

**Issue**: Missing TRIGGER conditions + extensive ADR-003 violations

**Actions**:
```bash
1. Update SKILL.md YAML frontmatter:
   - Add: TRIGGER when: "create skill", "update skill", "benchmark skill"
   - Add: DO NOT TRIGGER when: "just asking about skills"

2. Add docstrings to all 9 Python files:
   - run_eval.py
   - package_skill.py
   - quick_validate.py
   - improve_description.py
   - aggregate_benchmark.py
   - __init__.py
   - run_loop.py
   - generate_report.py
   - utils.py

3. Add type hints to 9 functions missing them

4. Test triggering accuracy
```

**Time estimate**: 2-3 hours
**Impact**: High - Core skill for skill development

---

## 🔶 Priority 1 - High (修复时间: 1-2 小时)

### 2. refers (80/100) ⚠️

**Issue**: SKILL.md completely missing

**Actions**:
```bash
1. Create SKILL.md with:
   - YAML frontmatter
   - TRIGGER/DO NOT TRIGGER conditions
   - Overview and usage documentation

2. Determine if this is an active skill or deprecated
   - If deprecated: Move to legacy/
   - If active: Full documentation needed
```

**Time estimate**: 30-60 minutes
**Impact**: Medium - Skill unusable without SKILL.md

---

### 3. eval-plan (76/100) ⚠️

**Issue**: Workflow skill missing WORKFLOW_PATTERNS compliance

**Actions**:
```bash
1. Add TaskCreate/TaskUpdate documentation to SKILL.md:
   - Document 7-step workflow
   - Add progress checklist template
   - Explain task management

2. Add WORKFLOW_PATTERNS reference section

3. Test with /work-issue integration
```

**Time estimate**: 45 minutes
**Impact**: High - Breaks /work-issue workflow

---

## 🔷 Priority 2 - Medium (修复时间: 30 分钟)

### 4. adr (87/100) ⚠️

**Issue**: Missing TRIGGER conditions

**Actions**:
```bash
1. Update SKILL.md description:
   - Add: TRIGGER when: "create adr", "record decision", "document architecture"
   - Add: DO NOT TRIGGER when: "just asking about decisions", "viewing existing ADRs"

2. Test triggering
```

**Time estimate**: 15 minutes
**Impact**: Low - Still usable, just less accurate

---

## 🔵 Priority 3 - Low (优化项，可选)

### Minor Warnings (不影响功能)

**Unexpected files** (6 occurrences):
- eval-plan: REFERENCE.md
- overview: requirements.txt
- sync: CONFLICT-HANDLING.md
- update-framework: 4 documentation files
- work-issue: REFERENCE.md

**Action**: Move to docs/ or keep (low priority)

**Missing module docstrings** (3 scripts):
- finish-issue: 3 helper scripts
- overview: 1 script

**Action**: Add docstrings (good practice, not critical)

---

## 📊 Success Metrics

### Target State
- ✅ All skills ≥90 score
- ✅ Zero critical ADR violations
- ✅ All workflow skills have TaskCreate/TaskUpdate docs

### Current Progress
- 16/20 skills at ≥90 (80%)
- Target: 20/20 (100%)
- Remaining work: ~4-5 hours

---

## 🎯 Implementation Order

**Day 1 (2-3 hours)**:
1. Fix skill-creator (P0) - 2-3 hours
2. Create refers SKILL.md (P1) - 30 min

**Day 2 (1 hour)**:
3. Fix eval-plan workflow docs (P1) - 45 min
4. Fix adr TRIGGER conditions (P2) - 15 min

**Day 3 (optional - 1 hour)**:
5. Add missing docstrings (P3)
6. Clean up unexpected files (P3)

---

## 🔧 Automated Fixes

Can be scripted:
```bash
# Add shebangs
for f in *.py; do
  if ! head -1 "$f" | grep -q "#!/usr/bin/env python3"; then
    sed -i '1i#!/usr/bin/env python3' "$f"
  fi
done

# Add basic docstrings template
# (would need manual completion)
```

---

## ✅ Verification

After fixes, run:
```bash
python .claude/skills/_scripts/audit_skills.py

# Target output:
# Total skills: 20
# ✅ Passed (≥90): 20
# ⚠️  Needs improvement: 0
# ❌ Failed: 0
# 📈 Average score: ≥95/100
```

---

## 📝 Notes

- Most skills (80%) already compliant ✅
- Main issues concentrated in 4 skills
- skill-creator needs most work (core tool, high priority)
- All fixes are straightforward documentation updates
- No code refactoring required (just docs + type hints)

**Total effort**: ~4-5 hours to achieve 100% compliance
