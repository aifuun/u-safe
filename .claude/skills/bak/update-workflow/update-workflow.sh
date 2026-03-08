#!/usr/bin/env bash
# update-workflow.sh - Sync workflow documentation between projects bidirectionally
# Part of AI Development Framework

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Workflow files to sync (relative paths from project root)
WORKFLOW_FILES=(
    "CLAUDE.md"
    ".claude/README.md"
    ".claude/WORKFLOW.md"
)

# Workflow directory
WORKFLOW_DIR=".claude/workflow"

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
SELECTED_FILES=()

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
            --files)
                IFS=',' read -ra SELECTED_FILES <<< "$2"
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
Update Workflow - Sync workflow documentation between projects

USAGE:
    update-workflow.sh --from <project> [OPTIONS]
    update-workflow.sh --to <project> [OPTIONS]

OPTIONS:
    --from <path>       Pull workflow from source project
    --to <path>         Push workflow to target project
    --dry-run           Preview changes without applying
    --force             Skip backup creation (overwrite directly)
    --files <list>      Only sync specified files (comma-separated)
    --help, -h          Show this help message

FILES:
    CLAUDE.md           Main project instructions
    README.md           Framework documentation (.claude/README.md)
    WORKFLOW.md         Quick start guide (.claude/WORKFLOW.md)
    workflow/           All planning templates (.claude/workflow/*.md)
    workflow/MAIN.md    Main workflow guide
    workflow/PLANNING.md Planning template
    workflow/TIER.md    Tiering system

EXAMPLES:
    # Pull all workflow from framework
    update-workflow.sh --from ~/dev/ai-dev

    # Push specific files to project
    update-workflow.sh --to ~/projects/my-app --files CLAUDE.md,workflow/

    # Preview update
    update-workflow.sh --from ~/dev/ai-dev --dry-run
EOF
}

# ============================================================================
# File Detection
# ============================================================================

list_workflow_files() {
    local project_dir="$1"

    declare -a files

    # Check main workflow files
    for file in "${WORKFLOW_FILES[@]}"; do
        if [[ -f "$project_dir/$file" ]]; then
            echo "$file"
        fi
    done

    # Check workflow directory
    if [[ -d "$project_dir/$WORKFLOW_DIR" ]]; then
        find "$project_dir/$WORKFLOW_DIR" -name "*.md" -type f | while read -r filepath; do
            # Convert to relative path from project root
            echo "${filepath#$project_dir/}"
        done
    fi
}

should_include_file() {
    local file="$1"

    # If no filter, include all
    if [[ ${#SELECTED_FILES[@]} -eq 0 ]]; then
        return 0
    fi

    # Check against filters
    for pattern in "${SELECTED_FILES[@]}"; do
        # Exact match
        if [[ "$file" == "$pattern" ]]; then
            return 0
        fi

        # Pattern match (e.g., "workflow/" matches ".claude/workflow/MAIN.md")
        if [[ "$file" == *"$pattern"* ]]; then
            return 0
        fi

        # Handle short names (e.g., "CLAUDE.md" matches "CLAUDE.md")
        local basename=$(basename "$file")
        if [[ "$basename" == "$pattern" ]]; then
            return 0
        fi
    done

    return 1
}

# ============================================================================
# File Comparison
# ============================================================================

compare_file() {
    local file_path="$1"      # e.g., "CLAUDE.md" or ".claude/workflow/MAIN.md"
    local source_dir="$2"
    local target_dir="$3"

    local source_file="$source_dir/$file_path"
    local target_file="$target_dir/$file_path"

    # Check existence
    if [[ ! -f "$target_file" ]]; then
        echo "NEW"
        return
    fi

    # Compare modification times
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

sync_workflow() {
    local mode="$1"
    local target_path="$2"

    # Resolve paths
    TARGET_PATH=$(cd "$target_path" && pwd)
    local source_dir target_dir

    if [[ "$mode" == "pull" ]]; then
        log_section "📥 Pulling workflow from $TARGET_PATH"
        source_dir="$TARGET_PATH"
        target_dir="$PROJECT_ROOT"
    else
        log_section "📤 Pushing workflow to $TARGET_PATH"
        source_dir="$PROJECT_ROOT"
        target_dir="$TARGET_PATH"
    fi

    # Validate paths
    if [[ ! -d "$source_dir" ]]; then
        log_error "Source directory not found: $source_dir"
        exit 1
    fi

    if [[ ! -d "$target_dir" ]] && [[ "$DRY_RUN" == "false" ]]; then
        log_error "Target directory not found: $target_dir"
        exit 1
    fi

    # Collect workflow files
    echo ""
    log_info "Scanning workflow files..."

    declare -a all_files
    while IFS= read -r file; do
        # Apply file filter
        if should_include_file "$file"; then
            all_files+=("$file")
        fi
    done < <(list_workflow_files "$source_dir")

    if [[ ${#all_files[@]} -eq 0 ]]; then
        log_warning "No workflow files found in source"
        exit 0
    fi

    log_success "Found ${#all_files[@]} workflow files in source"

    # Show selected files if filter applied
    if [[ ${#SELECTED_FILES[@]} -gt 0 ]]; then
        log_info "Selected files: ${SELECTED_FILES[*]}"
    fi

    # Analyze files
    echo ""
    log_info "Analyzing files..."
    echo ""

    declare -A file_status
    local new_count=0 newer_count=0 same_count=0 older_count=0

    for file in "${all_files[@]}"; do
        local status=$(compare_file "$file" "$source_dir" "$target_dir")
        file_status["$file"]="$status"

        case "$status" in
            NEW) ((new_count++)) ;;
            NEWER) ((newer_count++)) ;;
            SAME) ((same_count++)) ;;
            OLDER) ((older_count++)) ;;
        esac
    done

    # Display table
    echo "┌──────────────────────────────┬────────┬──────────────────┐"
    echo "│ File                         │ Status │ Action           │"
    echo "├──────────────────────────────┼────────┼──────────────────┤"

    for file in "${all_files[@]}"; do
        local status="${file_status[$file]}"
        local action=""
        local display_file="$file"

        # Truncate long filenames
        if [[ ${#display_file} -gt 28 ]]; then
            display_file="...${display_file: -25}"
        fi

        case "$status" in
            NEW)
                action="Add"
                printf "│ %-28s │ ${GREEN}NEW${NC}    │ %-16s │\n" "$display_file" "$action"
                ;;
            NEWER)
                action="Update"
                printf "│ %-28s │ ${YELLOW}NEWER${NC}  │ %-16s │\n" "$display_file" "$action"
                ;;
            SAME)
                action="Skip"
                printf "│ %-28s │ SAME   │ %-16s │\n" "$display_file" "$action"
                ;;
            OLDER)
                action="Skip (older)"
                printf "│ %-28s │ ${RED}OLDER${NC}  │ %-16s │\n" "$display_file" "$action"
                ;;
        esac
    done

    echo "└──────────────────────────────┴────────┴──────────────────┘"
    echo ""

    # Summary
    log_section "Summary"
    echo "New files: $new_count"
    echo "Updated files: $newer_count"
    echo "Unchanged: $same_count"
    [[ $older_count -gt 0 ]] && log_warning "Older in source: $older_count"
    echo ""

    local total_to_sync=$((new_count + newer_count))
    if [[ $total_to_sync -eq 0 ]]; then
        log_success "All workflow files are up to date!"
        return 0
    fi

    # Dry run exit
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "🔍 DRY RUN MODE - No changes made"
        log_info "Run without --dry-run to apply changes"
        return 0
    fi

    # Confirm
    echo -n "Proceed with syncing $total_to_sync files? (y/n) "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Cancelled by user"
        return 0
    fi

    # Copy files
    echo ""
    log_info "Syncing files..."
    echo ""

    for file in "${all_files[@]}"; do
        local status="${file_status[$file]}"
        if [[ "$status" == "NEW" ]] || [[ "$status" == "NEWER" ]]; then
            local source_file="$source_dir/$file"
            local target_file="$target_dir/$file"

            # Create directory if needed
            local target_parent=$(dirname "$target_file")
            mkdir -p "$target_parent"

            # Backup if exists (unless --force)
            if [[ -f "$target_file" ]] && [[ "$FORCE" == "false" ]]; then
                local backup_file="${target_file}.backup-$(date +%Y%m%d-%H%M%S)"
                cp "$target_file" "$backup_file"
            fi

            # Copy
            cp "$source_file" "$target_file"
            log_success "Synced: $file"
        fi
    done

    echo ""
    log_success "Sync complete! Updated $total_to_sync files"
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

    # Check current project has workflow files
    local workflow_count=$(list_workflow_files "$PROJECT_ROOT" | wc -l)
    if [[ $workflow_count -eq 0 ]]; then
        log_error "Current project has no workflow files"
        exit 1
    fi

    # Execute sync
    sync_workflow "$MODE" "$TARGET_PATH"
}

main "$@"
