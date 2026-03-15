#!/bin/bash
# Git status data collection module

collect_git_status() {
    local git_branch="unknown"
    local git_commit="N/A"
    local git_commit_msg="Git not available"
    local git_staged=0
    local git_unstaged=0
    local git_untracked=0

    if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
        git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        git_commit=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
        git_commit_msg=$(git log -1 --format="%s" 2>/dev/null || echo "No commit message")
        git_staged=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
        git_unstaged=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
        git_untracked=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Export as JSON
    cat <<EOF
{
  "branch": "$git_branch",
  "commit": "$git_commit",
  "commitMessage": "$git_commit_msg",
  "staged": $git_staged,
  "unstaged": $git_unstaged,
  "untracked": $git_untracked
}
EOF
}

collect_recent_commits() {
    if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
        git log --oneline -10 --format='{"hash":"%h","message":"%s","date":"%ar"}' 2>/dev/null | \
            awk 'BEGIN{print "["} {if(NR>1)print","; printf "%s", $0} END{print "]"}' || echo '[]'
    else
        echo '[]'
    fi
}
