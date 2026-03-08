#!/usr/bin/env bash
# update-pillars.sh - Sync Pillars between projects bidirectionally
# Part of AI Development Framework

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CURRENT_PILLARS_DIR="$PROJECT_ROOT/.prot/pillars"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# Utility Functions
# ============================================================================

log_info() { echo -e "${BLUE}ℹ${NC} $*"; }
log_success() { echo -e "${GREEN}✅${NC} $*"; }
log_warning() { echo -e "${YELLOW}⚠️${NC}  $*"; }
log_error() { echo -e "${RED}❌${NC} $*" >&2; }
log_section() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$*${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# ============================================================================
# Argument Parsing
# ============================================================================

MODE=""
TARGET_PATH=""
DRY_RUN=false
FORCE=false
SELECTED_PILLARS=()

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --from)
                MODE="pull"
                TARGET_PATH="$2"
                shift 2
                ;;
            --to)
                MODE="push"
                TARGET_PATH="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --pillars)
                IFS=',' read -ra SELECTED_PILLARS <<< "$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown argument: $1"
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << 'EOF'
Update Pillars - Sync Pillars between projects

USAGE:
    update-pillars.sh --from <project> [OPTIONS]
    update-pillars.sh --to <project> [OPTIONS]

OPTIONS:
    --from <path>       Pull Pillars from source project
    --to <path>         Push Pillars to target project
    --dry-run           Preview changes without applying
    --force             Skip backup creation (overwrite directly)
    --pillars A,B,K     Only sync specified Pillars
    --help, -h          Show this help message

EXAMPLES:
    # Pull all Pillars from framework
    update-pillars.sh --from ~/dev/ai-dev

    # Push specific Pillars to project
    update-pillars.sh --to ~/projects/my-app --pillars M,Q

    # Preview update
    update-pillars.sh --from ~/dev/ai-dev --dry-run
EOF
}

# ============================================================================
# Profile Detection
# ============================================================================

detect_profile_pillars() {
    local project_dir="$1"
    local profile_file="$project_dir/.framework-install"

    if [[ -f "$profile_file" ]]; then
        local profile=$(grep "^profile:" "$profile_file" 2>/dev/null | cut -d: -f2 | tr -d ' ')
        case "$profile" in
            minimal)
                echo "A B K"
                ;;
            node-lambda)
                echo "A B K M Q R"
                ;;
            react-aws)
                echo "A B K L M Q R"
                ;;
            *)
                # All Pillars in directory
                list_pillars_in_dir "$project_dir/.prot/pillars"
                ;;
        esac
    else
        # No profile, list all Pillars in directory
        list_pillars_in_dir "$project_dir/.prot/pillars"
    fi
}

list_pillars_in_dir() {
    local pillars_dir="$1"
    [[ ! -d "$pillars_dir" ]] && return

    find "$pillars_dir" -maxdepth 1 -type d -name "pillar-*" | while read -r dir; do
        basename "$dir" | sed 's/pillar-//' | tr '[:lower:]' '[:upper:]'
    done | tr '\n' ' '
}

# ============================================================================
# Pillar Comparison
# ============================================================================

compare_pillar() {
    local pillar_code="$1"
    local source_dir="$2"
    local target_dir="$3"

    local pillar_name="pillar-${pillar_code,,}"  # lowercase
    local source_pillar="$source_dir/$pillar_name"
    local target_pillar="$target_dir/$pillar_name"

    # Check existence
    if [[ ! -d "$target_pillar" ]]; then
        echo "NEW"
        return
    fi

    # Compare modification times (use any .md file in directory)
    local source_file=$(find "$source_pillar" -name "*.md" -type f | head -1)
    local target_file=$(find "$target_pillar" -name "*.md" -type f | head -1)

    if [[ -z "$source_file" ]] || [[ -z "$target_file" ]]; then
        echo "UNKNOWN"
        return
    fi

    local source_mtime=$(stat -f %m "$source_file" 2>/dev/null || stat -c %Y "$source_file" 2>/dev/null)
    local target_mtime=$(stat -f %m "$target_file" 2>/dev/null || stat -c %Y "$target_file" 2>/dev/null)

    if [[ $source_mtime -gt $target_mtime ]]; then
        echo "NEWER"
    elif [[ $source_mtime -lt $target_mtime ]]; then
        echo "OLDER"
    else
        echo "SAME"
    fi
}

# ============================================================================
# Main Sync Logic
# ============================================================================

sync_pillars() {
    local mode="$1"
    local target_path="$2"

    # Resolve paths
    TARGET_PATH=$(cd "$target_path" && pwd)
    local source_dir target_dir

    if [[ "$mode" == "pull" ]]; then
        log_section "📥 Pulling Pillars from $TARGET_PATH"
        source_dir="$TARGET_PATH/.prot/pillars"
        target_dir="$CURRENT_PILLARS_DIR"
    else
        log_section "📤 Pushing Pillars to $TARGET_PATH"
        source_dir="$CURRENT_PILLARS_DIR"
        target_dir="$TARGET_PATH/.prot/pillars"
    fi

    # Validate paths
    if [[ ! -d "$source_dir" ]]; then
        log_error "Source Pillars directory not found: $source_dir"
        exit 1
    fi

    if [[ ! -d "$target_dir" ]] && [[ "$DRY_RUN" == "false" ]]; then
        log_warning "Target Pillars directory not found: $target_dir"
        log_info "Creating directory..."
        mkdir -p "$target_dir"
    fi

    # Detect Pillars to sync
    local pillars_to_check
    if [[ ${#SELECTED_PILLARS[@]} -gt 0 ]]; then
        pillars_to_check="${SELECTED_PILLARS[*]}"
        log_info "Selected Pillars: $pillars_to_check"
    else
        # Detect from profile or scan directory
        if [[ "$mode" == "pull" ]]; then
            # Use target (current) project's profile
            pillars_to_check=$(detect_profile_pillars "$PROJECT_ROOT")
        else
            # Use all Pillars in source
            pillars_to_check=$(list_pillars_in_dir "$source_dir")
        fi
        log_info "Detected Pillars: $pillars_to_check"
    fi

    # Analyze Pillars
    echo ""
    log_info "Analyzing Pillars..."
    echo ""

    declare -A pillar_status
    local new_count=0 newer_count=0 same_count=0 older_count=0

    for pillar in $pillars_to_check; do
        local status=$(compare_pillar "$pillar" "$source_dir" "$target_dir")
        pillar_status["$pillar"]="$status"

        case "$status" in
            NEW) ((new_count++)) ;;
            NEWER) ((newer_count++)) ;;
            SAME) ((same_count++)) ;;
            OLDER) ((older_count++)) ;;
        esac
    done

    # Display table
    echo "┌─────────────┬────────┬──────────────────┐"
    echo "│ Pillar      │ Status │ Action           │"
    echo "├─────────────┼────────┼──────────────────┤"

    for pillar in $pillars_to_check; do
        local status="${pillar_status[$pillar]}"
        local action=""

        case "$status" in
            NEW)
                action="Add"
                printf "│ Pillar %-4s │ ${GREEN}NEW${NC}    │ ${action}%-14s │\n" "$pillar" ""
                ;;
            NEWER)
                action="Update"
                printf "│ Pillar %-4s │ ${YELLOW}NEWER${NC}  │ ${action}%-12s │\n" "$pillar" ""
                ;;
            SAME)
                action="Skip"
                printf "│ Pillar %-4s │ SAME   │ ${action}%-14s │\n" "$pillar" ""
                ;;
            OLDER)
                action="Skip (older)"
                printf "│ Pillar %-4s │ ${RED}OLDER${NC}  │ ${action}%-6s │\n" "$pillar" ""
                ;;
        esac
    done

    echo "└─────────────┴────────┴──────────────────┘"
    echo ""

    # Summary
    log_section "Summary"
    echo "New Pillars: $new_count"
    echo "Updated Pillars: $newer_count"
    echo "Unchanged: $same_count"
    [[ $older_count -gt 0 ]] && log_warning "Older in source: $older_count"
    echo ""

    local total_to_sync=$((new_count + newer_count))
    if [[ $total_to_sync -eq 0 ]]; then
        log_success "All Pillars are up to date!"
        return 0
    fi

    # Dry run exit
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "🔍 DRY RUN MODE - No changes made"
        log_info "Run without --dry-run to apply changes"
        return 0
    fi

    # Confirm
    echo -n "Proceed with syncing $total_to_sync Pillars? (y/n) "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Cancelled by user"
        return 0
    fi

    # Copy Pillars
    echo ""
    log_info "Syncing Pillars..."
    echo ""

    for pillar in $pillars_to_check; do
        local status="${pillar_status[$pillar]}"
        if [[ "$status" == "NEW" ]] || [[ "$status" == "NEWER" ]]; then
            local pillar_name="pillar-${pillar,,}"
            local source_path="$source_dir/$pillar_name"
            local target_path="$target_dir/$pillar_name"

            # Backup if exists (unless --force)
            if [[ -d "$target_path" ]] && [[ "$FORCE" == "false" ]]; then
                local backup_path="${target_path}.backup-$(date +%Y%m%d-%H%M%S)"
                log_info "Backing up: $pillar_name → $(basename "$backup_path")"
                cp -r "$target_path" "$backup_path"
            fi

            # Copy
            cp -r "$source_path" "$target_path"
            log_success "Synced: Pillar $pillar"
        fi
    done

    echo ""
    log_success "Sync complete! Updated $total_to_sync Pillars"
}

# ============================================================================
# Main
# ============================================================================

main() {
    parse_args "$@"

    # Validate arguments
    if [[ -z "$MODE" ]]; then
        log_error "Missing required argument: --from or --to"
        echo ""
        show_help
        exit 1
    fi

    if [[ -z "$TARGET_PATH" ]]; then
        log_error "Missing target path"
        exit 1
    fi

    # Check current project has Pillars
    if [[ ! -d "$CURRENT_PILLARS_DIR" ]]; then
        log_error "Current project has no Pillars directory: $CURRENT_PILLARS_DIR"
        exit 1
    fi

    # Execute sync
    sync_pillars "$MODE" "$TARGET_PATH"
}

main "$@"
