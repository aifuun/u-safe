#!/bin/bash
# Status - Project health and status reporter
# Main orchestrator script

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common library
source "$SCRIPT_DIR/lib/common.sh"

# Source all modules
source "$SCRIPT_DIR/modules/collect-git.sh"
source "$SCRIPT_DIR/modules/collect-framework.sh"
source "$SCRIPT_DIR/modules/collect-work.sh"
source "$SCRIPT_DIR/modules/detect-patterns.sh"
source "$SCRIPT_DIR/modules/calculate-health.sh"
source "$SCRIPT_DIR/modules/format-terminal.sh"
source "$SCRIPT_DIR/modules/format-html.sh"

# Parse arguments
TEXT_ONLY=false
HTML_ONLY=false
NO_OPEN=false

for arg in "$@"; do
    case $arg in
        --text-only)
            TEXT_ONLY=true
            shift || true
            ;;
        --html-only)
            HTML_ONLY=true
            shift || true
            ;;
        --no-open)
            NO_OPEN=true
            shift || true
            ;;
        --help|-h)
            cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Generate project status report with health metrics.

OPTIONS:
    --text-only      Skip HTML generation, terminal only
    --html-only      Generate HTML only, skip terminal output
    --no-open        Don't auto-open HTML in browser
    --help, -h       Show this help message

EXAMPLES:
    # Full status (terminal + HTML)
    $(basename "$0")

    # Terminal only (faster)
    $(basename "$0") --text-only

    # Generate HTML without opening
    $(basename "$0") --no-open

EOF
            exit 0
            ;;
        *)
            ;;
    esac
done

# Determine project root and navigate to it
PROJECT_ROOT=$(get_project_root)
cd "$PROJECT_ROOT"

# Get project name
PROJECT_NAME=$(get_project_name "$PROJECT_ROOT")

# ============================================================================
# Data Collection Phase
# ============================================================================

# Collect Git data
GIT_DATA=$(collect_git_status)
RECENT_COMMITS=$(collect_recent_commits)

# Collect Framework data
FRAMEWORK_DATA=$(collect_framework_info)

# Collect active work
WORK_PLANS=$(collect_active_plans)
WORK_ISSUES=$(collect_open_issues)

# Merge work data
if command -v jq &> /dev/null; then
    WORK_DATA=$(jq -n \
        --argjson plans "$WORK_PLANS" \
        --argjson issues "$WORK_ISSUES" \
        '{
            planCount: $plans.planCount,
            issueCount: $issues.issueCount,
            plans: $plans.plans,
            issues: $issues.issues
        }')
else
    WORK_DATA='{"planCount":0,"issueCount":0,"plans":[],"issues":[]}'
fi

# Detect code patterns
PATTERNS=$(detect_code_patterns)
TEST_COUNT=$(count_test_files)

# Extract values for health calculation
if command -v jq &> /dev/null; then
    FRAMEWORK_PROFILE=$(echo "$FRAMEWORK_DATA" | jq -r '.profile')
    GIT_STAGED=$(echo "$GIT_DATA" | jq -r '.staged')
    GIT_UNSTAGED=$(echo "$GIT_DATA" | jq -r '.unstaged')
    ACTIVE_PLANS=$(echo "$WORK_DATA" | jq -r '.plans')
else
    FRAMEWORK_PROFILE="unknown"
    GIT_STAGED=0
    GIT_UNSTAGED=0
    ACTIVE_PLANS="[]"
fi

# Calculate health score
HEALTH_SCORE=$(calculate_health_score "$FRAMEWORK_PROFILE" "$TEST_COUNT" "$PATTERNS" "$ACTIVE_PLANS" "$GIT_STAGED" "$GIT_UNSTAGED")

# Generate recommendations
RECOMMENDATIONS=$(generate_recommendations "$TEST_COUNT" "$GIT_UNSTAGED" "$FRAMEWORK_PROFILE")

# ============================================================================
# Output Phase
# ============================================================================

# Terminal output (unless --html-only)
if [ "$HTML_ONLY" = false ]; then
    format_terminal_output \
        "$PROJECT_NAME" \
        "$GIT_DATA" \
        "$FRAMEWORK_DATA" \
        "$WORK_DATA" \
        "$PATTERNS" \
        "$HEALTH_SCORE" \
        "$TEST_COUNT" \
        "$RECOMMENDATIONS"
fi

# HTML generation (unless --text-only)
if [ "$TEXT_ONLY" = false ]; then
    [ "$HTML_ONLY" = false ] && echo ""
    HTML_FILE=$(generate_html_report \
        "$PROJECT_NAME" \
        "$GIT_DATA" \
        "$FRAMEWORK_DATA" \
        "$WORK_DATA" \
        "$PATTERNS" \
        "$HEALTH_SCORE" \
        "$TEST_COUNT" \
        "$RECOMMENDATIONS" \
        "$RECENT_COMMITS")

    # Open in browser (unless --no-open)
    if [ "$NO_OPEN" = false ] && [ -n "$HTML_FILE" ]; then
        open_html_report "$HTML_FILE"
    fi
fi

# Success message
[ "$HTML_ONLY" = false ] && echo "" && log_success "Status report complete!"

exit 0
