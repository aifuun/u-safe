#!/bin/bash
# Collect comprehensive project information

collect_project_info() {
    local project_root="$1"
    local claude_md="$project_root/CLAUDE.md"

    # Start JSON object
    cat << 'EOF'
{
  "description": "",
  "coreConcept": "",
  "initialized": "unknown",
  "techStack": {
    "frontend": "",
    "backend": "",
    "auth": "",
    "iac": ""
  },
  "documentation": [],
  "completed": [],
  "architecture": {
    "adrCount": 0,
    "recentADRs": [],
    "patterns": []
  }
}
EOF
}

# Extract project description from CLAUDE.md
extract_description() {
    local claude_md="$1"
    if [ ! -f "$claude_md" ]; then
        echo "No project description available"
        return
    fi

    # Get product description (same line as "**Product**:")
    local desc=$(grep '^\*\*Product\*\*:' "$claude_md" 2>/dev/null | sed 's/^\*\*Product\*\*:[[:space:]]*//')

    # Limit to 300 characters for overview
    echo "$desc" | head -c 300
}

# Extract core concept
extract_core_concept() {
    local claude_md="$1"
    if [ ! -f "$claude_md" ]; then
        echo ""
        return
    fi

    # Get the token equation and explanation
    sed -n '/### 🎯 Core Concept/,/###/p' "$claude_md" 2>/dev/null | \
        grep -v '^###' | \
        grep -v '^\`\`\`' | \
        sed '/^$/d' | \
        head -4 | \
        tr '\n' ' '
}

# Extract tech stack
extract_tech_stack() {
    local claude_md="$1"
    if [ ! -f "$claude_md" ]; then
        echo '{"frontend":"N/A","backend":"N/A","auth":"N/A","iac":"N/A"}'
        return
    fi

    local frontend=$(grep '| \*\*Frontend\*\*' "$claude_md" 2>/dev/null | sed 's/.*| //' | sed 's/ |$//')
    local backend=$(grep '| \*\*Backend\*\*' "$claude_md" 2>/dev/null | sed 's/.*| //' | sed 's/ |$//')
    local auth=$(grep '| \*\*Auth\*\*' "$claude_md" 2>/dev/null | sed 's/.*| //' | sed 's/ |$//')
    local iac=$(grep '| \*\*IaC\*\*' "$claude_md" 2>/dev/null | sed 's/.*| //' | sed 's/ |$//')

    cat << EOF
{
  "frontend": "${frontend:-N/A}",
  "backend": "${backend:-N/A}",
  "auth": "${auth:-N/A}",
  "iac": "${iac:-N/A}"
}
EOF
}

# Extract documentation links
extract_documentation() {
    local claude_md="$1"
    if [ ! -f "$claude_md" ]; then
        echo '[]'
        return
    fi

    # Extract doc links from CLAUDE.md
    echo '['
    local first=true

    # PRD
    local prd=$(grep -o '\[PRD[^]]*\]([^)]*\.md)' "$claude_md" 2>/dev/null | head -1)
    if [ -n "$prd" ]; then
        local title=$(echo "$prd" | sed 's/\[\([^]]*\)\].*/\1/')
        local path=$(echo "$prd" | sed 's/.*(\([^)]*\)).*/\1/')
        [ "$first" = false ] && echo ','
        echo "    {\"title\":\"$title\",\"path\":\"$path\",\"type\":\"PRD\"}"
        first=false
    fi

    # Schema
    local schema=$(grep -o '\[.*Schema[^]]*\]([^)]*\.md)' "$claude_md" 2>/dev/null | head -1)
    if [ -n "$schema" ]; then
        local title=$(echo "$schema" | sed 's/\[\([^]]*\)\].*/\1/')
        local path=$(echo "$schema" | sed 's/.*(\([^)]*\)).*/\1/')
        [ "$first" = false ] && echo ','
        echo "    {\"title\":\"$title\",\"path\":\"$path\",\"type\":\"Architecture\"}"
        first=false
    fi

    # Roadmap
    local roadmap=$(grep -o '\[Roadmap[^]]*\]([^)]*\.md)' "$claude_md" 2>/dev/null | head -1)
    if [ -n "$roadmap" ]; then
        local title=$(echo "$roadmap" | sed 's/\[\([^]]*\)\].*/\1/')
        local path=$(echo "$roadmap" | sed 's/.*(\([^)]*\)).*/\1/')
        [ "$first" = false ] && echo ','
        echo "    {\"title\":\"$title\",\"path\":\"$path\",\"type\":\"Planning\"}"
        first=false
    fi

    echo '  ]'
}

# Extract completed work
extract_completed() {
    local claude_md="$1"
    if [ ! -f "$claude_md" ]; then
        echo '[]'
        return
    fi

    echo '['
    local completed=$(sed -n '/^\*\*Completed\*\*:/,/^---$/p' "$claude_md" 2>/dev/null | grep '^\- \*\*Issue' | head -5)
    local first=true

    while IFS= read -r line; do
        if [ -n "$line" ]; then
            local issue=$(echo "$line" | grep -o '#[0-9]\+')
            local title=$(echo "$line" | sed 's/.*Issue #[0-9]\+ ✅\*\*: *//' | sed 's/ (.*//')
            local desc=$(echo "$line" | sed 's/.*(\([^)]*\)).*/\1/')

            [ "$first" = false ] && echo ','
            echo "    {\"issue\":\"$issue\",\"title\":\"$title\",\"description\":\"$desc\"}"
            first=false
        fi
    done <<< "$completed"

    echo '  ]'
}

# Extract architecture info
extract_architecture() {
    local project_root="$1"
    local adr_dir="$project_root/docs/adr"

    # Count ADRs
    local adr_count=0
    if [ -d "$adr_dir" ]; then
        adr_count=$(ls -1 "$adr_dir/"[0-9]*.md 2>/dev/null | wc -l | tr -d ' ')
    fi

    echo '{'
    echo "  \"adrCount\": $adr_count,"
    echo '  "recentADRs": ['

    # Get latest 5 ADRs
    if [ -d "$adr_dir" ]; then
        local adrs=$(ls -t "$adr_dir/"[0-9]*.md 2>/dev/null | head -5)
        local first=true

        for adr in $adrs; do
            local num=$(basename "$adr" | grep -o '^[0-9]\+')
            local title=$(grep '^# ADR-' "$adr" 2>/dev/null | head -1 | sed 's/# ADR-[0-9]\+: *//')
            local status=$(grep -A 1 '^## Status' "$adr" 2>/dev/null | tail -1 | tr -d ' ')

            [ "$first" = false ] && echo ','
            echo "    {\"number\":\"$num\",\"title\":\"$title\",\"status\":\"$status\"}"
            first=false
        done
    fi

    echo '  ],'
    echo '  "patterns": ["Clean Architecture", "Headless UI", "Saga Pattern", "Nominal Types"]'
    echo '}'
}

# Main function that builds complete JSON
build_project_info_json() {
    local project_root="$1"
    local claude_md="$project_root/CLAUDE.md"

    local description=$(extract_description "$claude_md")
    local core_concept=$(extract_core_concept "$claude_md")
    local initialized=$(grep '^\*\*Initialized\*\*:' "$claude_md" 2>/dev/null | sed 's/.*: *//' || echo "unknown")

    cat << EOF
{
  "description": "$(echo "$description" | sed 's/"/\\"/g')",
  "coreConcept": "$(echo "$core_concept" | sed 's/"/\\"/g')",
  "initialized": "$initialized",
  "techStack": $(extract_tech_stack "$claude_md"),
  "documentation": $(extract_documentation "$claude_md"),
  "completed": $(extract_completed "$claude_md"),
  "architecture": $(extract_architecture "$project_root")
}
EOF
}

# If run directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    PROJECT_ROOT="${1:-$(pwd)}"
    build_project_info_json "$PROJECT_ROOT"
fi
