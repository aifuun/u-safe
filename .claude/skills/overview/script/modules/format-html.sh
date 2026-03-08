#!/bin/bash
# HTML report generation module

generate_html_report() {
    local project_name=$1
    local git_data=$2
    local framework_data=$3
    local work_data=$4
    local patterns=$5
    local health_score=$6
    local test_count=$7
    local recommendations=$8
    local project_info=$9
    local recent_commits=${10}

    # Create timestamp
    local timestamp=$(date -u +"%Y-%m-%dT%H-%M-%S")
    local readable_timestamp=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

    # Ensure reports directory exists
    mkdir -p "docs/reports"

    # Define output file
    local output_file="docs/reports/${project_name}-overview-${timestamp}.html"

    # Build JSON data object
    local json_data
    if command -v jq &> /dev/null; then
        # Extract git info
        local git_branch=$(echo "$git_data" | jq -r '.branch')
        local git_commit=$(echo "$git_data" | jq -r '.commit')
        local git_commit_msg=$(echo "$git_data" | jq -r '.commitMessage')
        local git_staged=$(echo "$git_data" | jq -r '.staged')
        local git_unstaged=$(echo "$git_data" | jq -r '.unstaged')
        local git_untracked=$(echo "$git_data" | jq -r '.untracked')

        # Extract framework info
        local fw_profile=$(echo "$framework_data" | jq -r '.profile')
        local fw_pillars=$(echo "$framework_data" | jq -r '.pillars')
        local fw_pillar_count=$(echo "$framework_data" | jq -r '.pillarCount')
        local fw_rule_count=$(echo "$framework_data" | jq -r '.ruleCount')
        local fw_command_count=$(echo "$framework_data" | jq -r '.commandCount')

        # Extract work info
        local work_plans=$(echo "$work_data" | jq -r '.plans')
        local work_issues=$(echo "$work_data" | jq -r '.issues')

        # Parse recent commits (already an array)
        local git_commits="$recent_commits"

        # Parse recommendations into structured format
        local recs_json='[]'
        if [ -n "$recommendations" ]; then
            recs_json=$(echo "$recommendations" | grep -v '^$' | sed 's/^- \[\([^]]*\)\] \(.*\)$/{"priority":"\1","title":"\2","estimate":""}/' | jq -s '. | map({priority: (.priority | ascii_downcase), title, estimate})')
        fi

        # Build complete data object
        json_data=$(jq -n \
            --arg projectName "$project_name" \
            --arg generatedAt "$readable_timestamp" \
            --arg gitBranch "$git_branch" \
            --arg gitCommit "$git_commit" \
            --arg gitCommitMsg "$git_commit_msg" \
            --argjson gitStaged "$git_staged" \
            --argjson gitUnstaged "$git_unstaged" \
            --argjson gitUntracked "$git_untracked" \
            --argjson gitCommits "$git_commits" \
            --arg fwProfile "$fw_profile" \
            --argjson fwPillars "$fw_pillars" \
            --argjson fwPillarCount "$fw_pillar_count" \
            --argjson fwRuleCount "$fw_rule_count" \
            --argjson fwCommandCount "$fw_command_count" \
            --argjson workPlans "$work_plans" \
            --argjson workIssues "$work_issues" \
            --argjson patterns "$patterns" \
            --argjson healthScore "$health_score" \
            --argjson recommendations "$recs_json" \
            --argjson projectInfo "$(echo "${project_info:-'{}'}" | jq -c .)" \
            '{
                projectName: $projectName,
                generatedAt: $generatedAt,
                git: {
                    branch: $gitBranch,
                    commit: $gitCommit,
                    commitMessage: $gitCommitMsg,
                    staged: $gitStaged,
                    unstaged: $gitUnstaged,
                    untracked: $gitUntracked,
                    recentCommits: $gitCommits
                },
                framework: {
                    profile: $fwProfile,
                    pillars: $fwPillars,
                    pillarCount: $fwPillarCount,
                    ruleCount: $fwRuleCount,
                    commandCount: $fwCommandCount
                },
                plans: $workPlans,
                issues: $workIssues,
                codeQuality: {
                    healthScore: $healthScore,
                    patterns: $patterns,
                    strengths: [],
                    observations: [],
                    recommendations: $recommendations
                },
                projectInfo: $projectInfo
            }')
    else
        log_error "jq is required for HTML generation"
        return 1
    fi

    # Read template
    local template_file="$SCRIPT_DIR/templates/combined-report.html"
    if [ ! -f "$template_file" ]; then
        log_error "Template file not found: $template_file"
        return 1
    fi

    # Write JSON to temp file
    local temp_json=$(mktemp)
    printf '%s' "$json_data" > "$temp_json"

    # Use awk with file reading - properly handle last line
    awk -v jsonfile="$temp_json" '
        {
            if (match($0, /\/\* DATA_PLACEHOLDER \*\//)) {
                # Split line at placeholder
                before = substr($0, 1, RSTART-1)
                after = substr($0, RSTART+RLENGTH)
                # Print before part
                printf "%s", before

                # Read and print JSON file - handle last line specially
                isFirst = 1
                while ((getline line < jsonfile) > 0) {
                    if (isFirst) {
                        printf "%s", line
                        isFirst = 0
                    } else {
                        printf "\n%s", line
                    }
                }
                close(jsonfile)

                # Print after part (usually semicolon)
                printf "%s\n", after
            } else {
                print
            }
        }
    ' "$template_file" > "$output_file"

    rm -f "$temp_json"

    if [ $? -eq 0 ] && [ -f "$output_file" ]; then
        log_success "HTML report generated: $output_file"
        # Return plain path without ANSI codes
        printf "%s" "$output_file"
    else
        log_error "Failed to generate HTML report"
        return 1
    fi
}

open_html_report() {
    local file_path=$1

    # Detect OS and open browser
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - suppress output
        open "$file_path" 2>/dev/null || log_warning "Could not auto-open browser"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open "$file_path" 2>/dev/null || log_warning "Could not auto-open browser"
        else
            log_warning "Could not auto-open browser. File: $file_path"
        fi
    else
        log_warning "Could not auto-open browser. File: $file_path"
    fi
}
