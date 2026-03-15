#!/bin/bash
# Common utilities for status scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✅${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC}  $*"
}

log_error() {
    echo -e "${RED}❌${NC} $*" >&2
}

log_section() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$*${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Determine project root
get_project_root() {
    local current_dir="$(pwd)"

    # Check if we're already in project root
    if [ -f "package.json" ] || [ -f ".framework-install" ] || [ -d ".claude" ]; then
        echo "$current_dir"
        return 0
    fi

    # Try to find project root by going up directories
    local dir="$current_dir"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/package.json" ] || [ -f "$dir/.framework-install" ] || [ -d "$dir/.claude" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done

    # Default to current directory
    echo "$current_dir"
}

# Get project name
get_project_name() {
    local project_root="${1:-$(pwd)}"
    local project_name=""

    # Try 1: Read from package.json
    if [ -f "$project_root/package.json" ]; then
        project_name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$project_root/package.json" | head -1 | sed 's/.*"\([^"]*\)".*/\1/' 2>/dev/null)
    fi

    # Try 2: Get from git remote URL (e.g., https://github.com/user/buffer.git → buffer)
    if [ -z "$project_name" ] && [ -d "$project_root/.git" ]; then
        project_name=$(cd "$project_root" && git remote get-url origin 2>/dev/null | sed 's/.*\/\([^/]*\)\.git$/\1/' | sed 's/.*\/\([^/]*\)$/\1/')
    fi

    # Try 3: Use directory name
    if [ -z "$project_name" ]; then
        project_name=$(basename "$project_root")
    fi

    # Fallback: Use default only if everything else fails
    if [ -z "$project_name" ]; then
        project_name="project"
    fi

    echo "$project_name"
}
