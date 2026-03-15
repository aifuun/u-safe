#!/bin/bash
# Code pattern detection module

detect_code_patterns() {
    local patterns='[]'
    local pattern_list=""

    # Detect nominal types
    grep -rq "unique symbol" src/ 2>/dev/null && pattern_list="$pattern_list\"nominal-types\"," || true

    # Detect airlock validation
    grep -rq "airlock" src/ 2>/dev/null && pattern_list="$pattern_list\"airlock\"," || true

    # Detect saga pattern
    grep -rq "Saga" src/ 2>/dev/null && pattern_list="$pattern_list\"saga\"," || true

    # Detect headless UI
    { [ -d "src/headless" ] || [ -d "packages/frontend/src/headless" ]; } && pattern_list="$pattern_list\"headless-ui\"," || true

    # Build JSON array
    if [ -n "$pattern_list" ]; then
        pattern_list="${pattern_list%,}"
        patterns="[$pattern_list]"
    fi

    echo "$patterns"
}

count_test_files() {
    local test_count=0

    if [ -d "tests" ]; then
        test_count=$(find tests -type f \( -name "*.test.*" -o -name "*.spec.*" \) 2>/dev/null | wc -l | tr -d ' ')
    fi

    echo "$test_count"
}
