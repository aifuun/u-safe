#!/bin/bash
# Framework configuration data collection module

collect_framework_info() {
    local profile="Not installed"
    local pillars='[]'
    local pillar_count=0
    local rule_count=0
    local command_count=0

    # Detect framework profile
    if [ -f ".framework-install" ]; then
        if head -1 .framework-install | grep -q '^[{\[]'; then
            # JSON format
            if command -v jq &> /dev/null; then
                profile=$(jq -r '.profile // "unknown"' .framework-install 2>/dev/null || echo "unknown")
                local pillars_json=$(jq -r '.pillars[]? // empty' .framework-install 2>/dev/null | tr '\n' ' ')
                if [ -n "$pillars_json" ]; then
                    pillar_count=$(echo "$pillars_json" | wc -w | tr -d ' ')
                    pillars="["
                    local first=true
                    for pillar in $pillars_json; do
                        [ "$first" = true ] && first=false || pillars="$pillars,"
                        pillars="$pillars\"$pillar\""
                    done
                    pillars="$pillars]"
                fi
            fi
        else
            # Text format
            profile=$(grep '^\*\*Profile\*\*:' .framework-install | sed 's/\*\*Profile\*\*:[[:space:]]*//' | tr -d '\r' || echo "unknown")
        fi

        # Detect Pillars from directory if not found in metadata
        if [ "$pillar_count" -eq 0 ] && [ -d ".prot/pillars" ]; then
            local pillar_ids=$(find .prot/pillars -type d -name "pillar-*" 2>/dev/null | sed 's/.*pillar-\([a-z]\).*/\1/' | tr '[:lower:]' '[:upper:]' | sort -u)
            if [ -n "$pillar_ids" ]; then
                pillars="["
                local first=true
                for pillar in $pillar_ids; do
                    [ "$first" = true ] && first=false || pillars="$pillars,"
                    pillars="$pillars\"$pillar\""
                done
                pillars="$pillars]"
                pillar_count=$(echo "$pillar_ids" | wc -l | tr -d ' ')
            fi
        fi
    fi

    # Count rules and commands
    [ -d ".claude/rules" ] && rule_count=$(find .claude/rules -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    [ -d ".claude/commands" ] && command_count=$(find .claude/commands -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

    # Export as JSON
    cat <<EOF
{
  "profile": "$profile",
  "pillars": $pillars,
  "pillarCount": $pillar_count,
  "ruleCount": $rule_count,
  "commandCount": $command_count
}
EOF
}
