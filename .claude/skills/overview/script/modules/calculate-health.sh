#!/bin/bash
# Health score calculation module

calculate_health_score() {
    local framework_profile="$1"
    local test_count="$2"
    local patterns="$3"
    local active_plans="$4"
    local git_staged="$5"
    local git_unstaged="$6"

    local health_score=0

    # Framework installed: +20
    [ "$framework_profile" != "Not installed" ] && health_score=$((health_score + 20)) || true

    # Has tests: +20
    [ "$test_count" -gt 0 ] && health_score=$((health_score + 20)) || true

    # Uses nominal types: +15
    echo "$patterns" | grep -q "nominal-types" && health_score=$((health_score + 15)) || true

    # Uses airlock: +15
    echo "$patterns" | grep -q "airlock" && health_score=$((health_score + 15)) || true

    # Has active plans: +10
    [ "$active_plans" != "[]" ] && health_score=$((health_score + 10)) || true

    # Clean git status: +10
    [ "$git_staged" -eq 0 ] && [ "$git_unstaged" -eq 0 ] && health_score=$((health_score + 10)) || true

    # Has documentation: +10
    { [ -f "README.md" ] && [ -d "docs" ]; } && health_score=$((health_score + 10)) || true

    echo "$health_score"
}

generate_recommendations() {
    local test_count="$1"
    local git_unstaged="$2"
    local framework_profile="$3"

    local recommendations=""

    # No tests
    [ "$test_count" -eq 0 ] && recommendations="${recommendations}- [High] Add test coverage (2-4h)"$'\n' || true

    # Too many unstaged changes
    [ "$git_unstaged" -gt 5 ] && recommendations="${recommendations}- [Medium] Commit unstaged changes (30min)"$'\n' || true

    # Framework not installed
    [ "$framework_profile" = "Not installed" ] && recommendations="${recommendations}- [High] Install framework (1h)"$'\n' || true

    echo "$recommendations"
}
