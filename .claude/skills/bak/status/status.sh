#!/bin/bash

# Status Skill - Dual output: Terminal text + HTML report
# Usage: ./status.sh [--text-only] [--html-only] [--no-open]

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
TEXT_ONLY=false
HTML_ONLY=false
NO_OPEN=false

for arg in "$@"; do
    case $arg in
        --text-only)
            TEXT_ONLY=true
            shift
            ;;
        --html-only)
            HTML_ONLY=true
            shift
            ;;
        --no-open)
            NO_OPEN=true
            shift
            ;;
        *)
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine project root
if [ -f "package.json" ] || [ -f ".framework-install" ] || [ -d ".claude" ]; then
    PROJECT_ROOT="$(pwd)"
else
    PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"
    cd "$PROJECT_ROOT"
fi

# Get Project Name
PROJECT_NAME="ai-dev"
if [ -f "package.json" ]; then
    PROJECT_NAME=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' package.json | head -1 | sed 's/.*"\([^"]*\)".*/\1/' || echo "ai-dev")
fi

# Collect Git Data
GIT_BRANCH="unknown"
GIT_COMMIT="N/A"
GIT_COMMIT_MSG="Git not available"
GIT_STAGED=0
GIT_UNSTAGED=0
GIT_UNTRACKED=0

if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
    GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
    GIT_COMMIT_MSG=$(git log -1 --format="%s" 2>/dev/null || echo "No commit message")
    GIT_STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
    GIT_UNSTAGED=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
    GIT_UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
fi

# Collect Recent Commits
RECENT_COMMITS='[]'
RECENT_COMMITS_TEXT=""
if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
    RECENT_COMMITS=$(git log --oneline -10 --format='{"hash":"%h","message":"%s","date":"%ar"}' 2>/dev/null | \
        awk 'BEGIN{print "["} {if(NR>1)print","; printf "%s", $0} END{print "]"}' || echo '[]')
    RECENT_COMMITS_TEXT=$(git log --oneline -5 --format="- %h %s (%ar)" 2>/dev/null || echo "No commits")
fi

# Collect Framework Data
FRAMEWORK_PROFILE="Not installed"
FRAMEWORK_PILLARS='[]'
PILLAR_COUNT=0

if [ -f ".framework-install" ]; then
    if head -1 .framework-install | grep -q '^[{\[]'; then
        if command -v jq &> /dev/null; then
            FRAMEWORK_PROFILE=$(jq -r '.profile // "unknown"' .framework-install 2>/dev/null || echo "unknown")
            PILLARS_JSON=$(jq -r '.pillars[]? // empty' .framework-install 2>/dev/null | tr '\n' ' ')
            if [ -n "$PILLARS_JSON" ]; then
                PILLAR_COUNT=$(echo "$PILLARS_JSON" | wc -w | tr -d ' ')
                FRAMEWORK_PILLARS="["
                FIRST=true
                for pillar in $PILLARS_JSON; do
                    [ "$FIRST" = true ] && FIRST=false || FRAMEWORK_PILLARS="$FRAMEWORK_PILLARS,"
                    FRAMEWORK_PILLARS="$FRAMEWORK_PILLARS\"$pillar\""
                done
                FRAMEWORK_PILLARS="$FRAMEWORK_PILLARS]"
            fi
        fi
    else
        FRAMEWORK_PROFILE=$(grep '^\*\*Profile\*\*:' .framework-install | sed 's/\*\*Profile\*\*:[[:space:]]*//' | tr -d '\r' || echo "unknown")
    fi

    if [ "$PILLAR_COUNT" -eq 0 ] && [ -d ".prot/pillars" ]; then
        PILLAR_IDS=$(find .prot/pillars -type d -name "pillar-*" 2>/dev/null | sed 's/.*pillar-\([a-z]\).*/\1/' | tr '[:lower:]' '[:upper:]' | sort -u)
        if [ -n "$PILLAR_IDS" ]; then
            FRAMEWORK_PILLARS="["
            FIRST=true
            for pillar in $PILLAR_IDS; do
                [ "$FIRST" = true ] && FIRST=false || FRAMEWORK_PILLARS="$FRAMEWORK_PILLARS,"
                FRAMEWORK_PILLARS="$FRAMEWORK_PILLARS\"$pillar\""
            done
            FRAMEWORK_PILLARS="$FRAMEWORK_PILLARS]"
            PILLAR_COUNT=$(echo "$PILLAR_IDS" | wc -l | tr -d ' ')
        fi
    fi
fi

PILLARS_TEXT=$(echo "$FRAMEWORK_PILLARS" | tr -d '[]"' | tr ',' ' ')

# Count Rules and Commands
RULE_COUNT=0
COMMAND_COUNT=0
[ -d ".claude/rules" ] && RULE_COUNT=$(find .claude/rules -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
[ -d ".claude/commands" ] && COMMAND_COUNT=$(find .claude/commands -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

# Collect Plans and Issues
ACTIVE_PLANS='[]'
PLAN_COUNT=0
PLANS_TEXT="No active plans"
if [ -d ".claude/plans/active" ]; then
    PLAN_FILES=$(ls -1 .claude/plans/active/*.md 2>/dev/null || echo "")
    if [ -n "$PLAN_FILES" ]; then
        ACTIVE_PLANS="["
        PLANS_TEXT=""
        FIRST=true
        for plan_file in $PLAN_FILES; do
            [ "$FIRST" = true ] && FIRST=false || ACTIVE_PLANS="$ACTIVE_PLANS,"
            PLAN_NAME=$(basename "$plan_file" .md)
            ACTIVE_PLANS="$ACTIVE_PLANS{\"name\":\"$PLAN_NAME\",\"status\":\"active\",\"progress\":\"unknown\"}"
            PLANS_TEXT="${PLANS_TEXT}- $PLAN_NAME"$'\n'
            PLAN_COUNT=$((PLAN_COUNT + 1))
        done
        ACTIVE_PLANS="$ACTIVE_PLANS]"
    fi
fi

OPEN_ISSUES='[]'
ISSUE_COUNT=0
ISSUES_TEXT="No open issues"
if command -v gh &> /dev/null; then
    OPEN_ISSUES=$(gh issue list --state open --limit 10 --json number,title,state 2>/dev/null || echo '[]')
    ISSUE_COUNT=$(echo "$OPEN_ISSUES" | grep -o '"number"' | wc -l | tr -d ' ')
    [ "$ISSUE_COUNT" -gt 0 ] && ISSUES_TEXT=$(gh issue list --state open --limit 5 --json number,title --template '{{range .}}- #{{.number}}: {{.title}}{{"\n"}}{{end}}' 2>/dev/null || echo "")
fi

# Detect Patterns
PATTERNS='[]'
PATTERN_LIST=""
PATTERNS_TEXT=""

grep -rq "unique symbol" src/ 2>/dev/null && PATTERN_LIST="$PATTERN_LIST\"nominal-types\"," && PATTERNS_TEXT="${PATTERNS_TEXT}nominal-types, "
grep -rq "airlock" src/ 2>/dev/null && PATTERN_LIST="$PATTERN_LIST\"airlock\"," && PATTERNS_TEXT="${PATTERNS_TEXT}airlock, "
grep -rq "Saga" src/ 2>/dev/null && PATTERN_LIST="$PATTERN_LIST\"saga\"," && PATTERNS_TEXT="${PATTERNS_TEXT}saga, "
{ [ -d "src/headless" ] || [ -d "packages/frontend/src/headless" ]; } && PATTERN_LIST="$PATTERN_LIST\"headless-ui\"," && PATTERNS_TEXT="${PATTERNS_TEXT}headless-ui, "

if [ -n "$PATTERN_LIST" ]; then
    PATTERN_LIST="${PATTERN_LIST%,}"
    PATTERNS="[$PATTERN_LIST]"
    PATTERNS_TEXT="${PATTERNS_TEXT%, }"
else
    PATTERNS_TEXT="None detected"
fi

# Calculate Health Score
HEALTH_SCORE=0
[ "$FRAMEWORK_PROFILE" != "Not installed" ] && HEALTH_SCORE=$((HEALTH_SCORE + 20))

TEST_COUNT=0
[ -d "tests" ] && TEST_COUNT=$(find tests -type f \( -name "*.test.*" -o -name "*.spec.*" \) 2>/dev/null | wc -l | tr -d ' ')
[ "$TEST_COUNT" -gt 0 ] && HEALTH_SCORE=$((HEALTH_SCORE + 20))

echo "$PATTERNS" | grep -q "nominal-types" && HEALTH_SCORE=$((HEALTH_SCORE + 15))
echo "$PATTERNS" | grep -q "airlock" && HEALTH_SCORE=$((HEALTH_SCORE + 15))
[ "$ACTIVE_PLANS" != "[]" ] && HEALTH_SCORE=$((HEALTH_SCORE + 10))
[ "$GIT_STAGED" -eq 0 ] && [ "$GIT_UNSTAGED" -eq 0 ] && HEALTH_SCORE=$((HEALTH_SCORE + 10))
{ [ -f "README.md" ] && [ -d "docs" ]; } && HEALTH_SCORE=$((HEALTH_SCORE + 10))

# Generate Strengths, Observations, Recommendations
STRENGTHS='[]'
OBSERVATIONS='[]'
RECOMMENDATIONS='[]'
STRENGTHS_TEXT=""
RECOMMENDATIONS_TEXT=""

STRENGTH_LIST=""
[ "$FRAMEWORK_PROFILE" != "Not installed" ] && STRENGTH_LIST="$STRENGTH_LIST\"Framework installed ($FRAMEWORK_PROFILE)\"," && STRENGTHS_TEXT="${STRENGTHS_TEXT}- Framework installed ($FRAMEWORK_PROFILE)"$'\n'
[ "$TEST_COUNT" -gt 0 ] && STRENGTH_LIST="$STRENGTH_LIST\"$TEST_COUNT test files\"," && STRENGTHS_TEXT="${STRENGTHS_TEXT}- $TEST_COUNT test files"$'\n'
echo "$PATTERNS" | grep -q "nominal-types" && STRENGTH_LIST="$STRENGTH_LIST\"Nominal typing\"," && STRENGTHS_TEXT="${STRENGTHS_TEXT}- Nominal typing"$'\n'
echo "$PATTERNS" | grep -q "airlock" && STRENGTH_LIST="$STRENGTH_LIST\"Airlock validation\"," && STRENGTHS_TEXT="${STRENGTHS_TEXT}- Airlock validation"$'\n'

[ -n "$STRENGTH_LIST" ] && STRENGTH_LIST="${STRENGTH_LIST%,}" && STRENGTHS="[$STRENGTH_LIST]"

OBS_LIST=""
[ "$GIT_UNSTAGED" -gt 0 ] && OBS_LIST="$OBS_LIST\"$GIT_UNSTAGED unstaged files\","
[ "$RULE_COUNT" -gt 0 ] && OBS_LIST="$OBS_LIST\"$RULE_COUNT rules available\","
[ "$COMMAND_COUNT" -gt 0 ] && OBS_LIST="$OBS_LIST\"$COMMAND_COUNT commands\","
[ -n "$OBS_LIST" ] && OBS_LIST="${OBS_LIST%,}" && OBSERVATIONS="[$OBS_LIST]"

REC_LIST=""
[ "$TEST_COUNT" -eq 0 ] && REC_LIST="$REC_LIST{\"priority\":\"high\",\"title\":\"Add tests\",\"estimate\":\"2-4h\"}," && RECOMMENDATIONS_TEXT="${RECOMMENDATIONS_TEXT}- [High] Add test coverage (2-4h)"$'\n'
[ "$GIT_UNSTAGED" -gt 5 ] && REC_LIST="$REC_LIST{\"priority\":\"medium\",\"title\":\"Commit changes\",\"estimate\":\"30min\"}," && RECOMMENDATIONS_TEXT="${RECOMMENDATIONS_TEXT}- [Medium] Commit unstaged changes (30min)"$'\n'
[ "$FRAMEWORK_PROFILE" = "Not installed" ] && REC_LIST="$REC_LIST{\"priority\":\"high\",\"title\":\"Install framework\",\"estimate\":\"1h\"}," && RECOMMENDATIONS_TEXT="${RECOMMENDATIONS_TEXT}- [High] Install framework (1h)"$'\n'
[ -n "$REC_LIST" ] && REC_LIST="${REC_LIST%,}" && RECOMMENDATIONS="[$REC_LIST]"

# Terminal Output (unless --html-only)
if [ "$HTML_ONLY" = false ]; then
    echo ""
    echo -e "${CYAN}# 📊 Project Status - $PROJECT_NAME${NC}"
    echo ""
    echo -e "${BLUE}## 🔀 Git${NC}"
    echo "Branch: $GIT_BRANCH"
    echo "Commit: $GIT_COMMIT - \"$GIT_COMMIT_MSG\""
    if [ "$GIT_STAGED" -eq 0 ] && [ "$GIT_UNSTAGED" -eq 0 ] && [ "$GIT_UNTRACKED" -eq 0 ]; then
        echo -e "Status: ${GREEN}Clean${NC}"
    else
        echo "Status: $GIT_STAGED staged, $GIT_UNSTAGED unstaged, $GIT_UNTRACKED untracked"
    fi
    echo ""
    echo -e "${BLUE}## ⚙️ Framework${NC}"
    echo "Profile: $FRAMEWORK_PROFILE"
    [ "$PILLAR_COUNT" -gt 0 ] && echo "Pillars: $PILLAR_COUNT enabled ($PILLARS_TEXT)"
    echo "Health Score: $HEALTH_SCORE/100"
    echo ""
    echo -e "${BLUE}## 📋 Active Work${NC}"
    echo "Plans: $PLAN_COUNT active"
    [ "$PLAN_COUNT" -gt 0 ] && echo "$PLANS_TEXT"
    echo "Issues: $ISSUE_COUNT open"
    [ "$ISSUE_COUNT" -gt 0 ] && echo "$ISSUES_TEXT"
    echo ""
    echo -e "${BLUE}## 📈 Recent Commits (Last 5)${NC}"
    echo "$RECENT_COMMITS_TEXT"
    echo ""
    echo -e "${BLUE}## ✨ Code Quality${NC}"
    echo "Patterns: $PATTERNS_TEXT"
    [ -n "$STRENGTHS_TEXT" ] && echo "Strengths:" && echo "$STRENGTHS_TEXT"
    [ -n "$RECOMMENDATIONS_TEXT" ] && echo "Recommendations:" && echo "$RECOMMENDATIONS_TEXT"
    echo ""
fi

# HTML Generation (unless --text-only)
if [ "$TEXT_ONLY" = false ]; then
    GENERATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    EXPORT_DATA=$(cat <<EOF
{
  "projectName": "$PROJECT_NAME",
  "generatedAt": "$GENERATED_AT",
  "git": {
    "branch": "$GIT_BRANCH",
    "commit": "$GIT_COMMIT",
    "commitMessage": "$GIT_COMMIT_MSG",
    "staged": $GIT_STAGED,
    "unstaged": $GIT_UNSTAGED,
    "untracked": $GIT_UNTRACKED,
    "recentCommits": $RECENT_COMMITS
  },
  "framework": {
    "profile": "$FRAMEWORK_PROFILE",
    "pillars": $FRAMEWORK_PILLARS,
    "pillarCount": $PILLAR_COUNT,
    "ruleCount": $RULE_COUNT,
    "commandCount": $COMMAND_COUNT
  },
  "codeQuality": {
    "healthScore": $HEALTH_SCORE,
    "patterns": $PATTERNS,
    "strengths": $STRENGTHS,
    "observations": $OBSERVATIONS,
    "recommendations": $RECOMMENDATIONS
  },
  "plans": $ACTIVE_PLANS,
  "issues": $OPEN_ISSUES
}
EOF
)

    TEMPLATE_FILE="$SCRIPT_DIR/templates/combined-report.html"
    if [ ! -f "$TEMPLATE_FILE" ]; then
        echo "❌ Error: Template not found at $TEMPLATE_FILE"
        exit 1
    fi

    HTML_CONTENT=""
    while IFS= read -r line; do
        if echo "$line" | grep -q "/\* DATA_PLACEHOLDER \*/"; then
            prefix="${line%%/\* DATA_PLACEHOLDER \*/*}"
            suffix="${line##*/\* DATA_PLACEHOLDER \*/}"
            HTML_CONTENT="${HTML_CONTENT}${prefix}${EXPORT_DATA}${suffix}"$'\n'
        else
            HTML_CONTENT="${HTML_CONTENT}${line}"$'\n'
        fi
    done < "$TEMPLATE_FILE"

    mkdir -p docs/reports
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H-%M-%S" | tr ':' '-')
    OUTPUT_FILE="docs/reports/${PROJECT_NAME}-combined-${TIMESTAMP}.html"
    echo "$HTML_CONTENT" > "$OUTPUT_FILE"
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | awk '{print $1}')

    [ "$HTML_ONLY" = false ] && echo "---" && echo ""
    echo -e "${GREEN}📄 Full report: $OUTPUT_FILE${NC} (Size: $FILE_SIZE)"

    if [ "$NO_OPEN" = false ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "$OUTPUT_FILE" 2>/dev/null && echo "Opening in browser..." || true
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open "$OUTPUT_FILE" 2>/dev/null && echo "Opening in browser..." || true
        fi
    fi
fi

[ "$HTML_ONLY" = false ] && echo "" && echo -e "${GREEN}✅ Ready to continue? Run: /next${NC}"
exit 0
