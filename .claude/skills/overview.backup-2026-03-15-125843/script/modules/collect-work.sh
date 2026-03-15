#!/bin/bash
# Active work (plans and issues) data collection module

collect_active_plans() {
    local plans='[]'
    local plan_count=0

    if [ -d ".claude/plans/active" ]; then
        local plan_files=$(ls -1 .claude/plans/active/*.md 2>/dev/null || echo "")
        if [ -n "$plan_files" ]; then
            plans="["
            local first=true
            for plan_file in $plan_files; do
                [ "$first" = true ] && first=false || plans="$plans,"
                local plan_name=$(basename "$plan_file" .md)
                plans="$plans{\"name\":\"$plan_name\",\"status\":\"active\",\"progress\":\"unknown\"}"
                plan_count=$((plan_count + 1))
            done
            plans="$plans]"
        fi
    fi

    # Export as JSON
    cat <<EOF
{
  "plans": $plans,
  "planCount": $plan_count
}
EOF
}

collect_open_issues() {
    local issues='[]'
    local issue_count=0

    if command -v gh &> /dev/null; then
        issues=$(gh issue list --state open --limit 10 --json number,title,state 2>/dev/null || echo '[]')
        issue_count=$(echo "$issues" | grep -o '"number"' | wc -l | tr -d ' ')
    fi

    # Export as JSON
    cat <<EOF
{
  "issues": $issues,
  "issueCount": $issue_count
}
EOF
}
