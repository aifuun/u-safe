#!/bin/bash
# Terminal output formatting module

format_terminal_output() {
    local project_name="$1"
    local git_data="$2"
    local framework_data="$3"
    local work_data="$4"
    local patterns="$5"
    local health_score="$6"
    local test_count="$7"
    local recommendations="$8"

    # Parse JSON data (using jq if available, or simple grep)
    local git_branch git_commit git_commit_msg git_staged git_unstaged git_untracked
    local framework_profile pillar_count pillars_text
    local plan_count issue_count

    if command -v jq &> /dev/null; then
        git_branch=$(echo "$git_data" | jq -r '.branch')
        git_commit=$(echo "$git_data" | jq -r '.commit')
        git_commit_msg=$(echo "$git_data" | jq -r '.commitMessage')
        git_staged=$(echo "$git_data" | jq -r '.staged')
        git_unstaged=$(echo "$git_data" | jq -r '.unstaged')
        git_untracked=$(echo "$git_data" | jq -r '.untracked')

        framework_profile=$(echo "$framework_data" | jq -r '.profile')
        pillar_count=$(echo "$framework_data" | jq -r '.pillarCount')
        pillars_text=$(echo "$framework_data" | jq -r '.pillars | join(", ")')

        plan_count=$(echo "$work_data" | jq -r '.planCount')
        issue_count=$(echo "$work_data" | jq -r '.issueCount')
    else
        # Fallback without jq
        git_branch=$(echo "$git_data" | grep -o '"branch":"[^"]*"' | cut -d'"' -f4)
        git_commit=$(echo "$git_data" | grep -o '"commit":"[^"]*"' | cut -d'"' -f4)
        git_commit_msg=$(echo "$git_data" | grep -o '"commitMessage":"[^"]*"' | cut -d'"' -f4)
        framework_profile="unknown"
        pillar_count="0"
        plan_count="0"
        issue_count="0"
    fi

    # Display output
    echo ""
    echo -e "${CYAN}# 📊 Project Overview - $project_name${NC}"
    echo ""
    echo -e "${BLUE}## 🔀 Git${NC}"
    echo "Branch: $git_branch"
    echo "Commit: $git_commit - \"$git_commit_msg\""
    if [ "$git_staged" -eq 0 ] && [ "$git_unstaged" -eq 0 ] && [ "$git_untracked" -eq 0 ]; then
        echo -e "Status: ${GREEN}Clean${NC}"
    else
        echo "Status: $git_staged staged, $git_unstaged unstaged, $git_untracked untracked"
    fi
    echo ""
    echo -e "${BLUE}## ⚙️ Framework${NC}"
    echo "Profile: $framework_profile"
    [ "$pillar_count" -gt 0 ] && echo "Pillars: $pillar_count enabled ($pillars_text)"
    echo "Health Score: $health_score/100"
    echo ""
    echo -e "${BLUE}## 📋 Active Work${NC}"
    echo "Plans: $plan_count active"
    echo "Issues: $issue_count open"
    echo ""
    echo -e "${BLUE}## ✨ Code Quality${NC}"
    echo "Patterns: $patterns"
    echo "Tests: $test_count files"
    [ -n "$recommendations" ] && echo "Recommendations:" && echo "$recommendations"
    echo ""
}
