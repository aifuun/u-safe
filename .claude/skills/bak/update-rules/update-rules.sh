#!/usr/bin/env bash
# update-rules.sh - Sync technical rules between projects bidirectionally
# Part of AI Development Framework

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CURRENT_RULES_DIR="$PROJECT_ROOT/.claude/rules"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Valid categories
VALID_CATEGORIES=("core" "architecture" "languages" "frontend" "backend" "infrastructure" "development")

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
SELECTED_CATEGORIES=()

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
            --categories)
                IFS=',' read -ra SELECTED_CATEGORIES <<< "$2"
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
Update Rules - Sync technical rules between projects

USAGE:
    update-rules.sh --from <project> [OPTIONS]
    update-rules.sh --to <project> [OPTIONS]

OPTIONS:
    --from <path>         Pull rules from source project
    --to <path>           Push rules to target project
    --dry-run             Preview changes without applying
    --force               Skip backup creation (overwrite directly)
    --categories <list>   Only sync specified categories (comma-separated)
    --help, -h            Show this help message

CATEGORIES:
    core, architecture, languages, frontend, backend, infrastructure, development

EXAMPLES:
    # Pull all rules from framework
    update-rules.sh --from ~/dev/ai-dev

    # Push specific categories to project
    update-rules.sh --to ~/projects/my-app --categories frontend,backend

    # Preview update
    update-rules.sh --from ~/dev/ai-dev --dry-run
EOF
}

# ============================================================================
# Category Functions
# ============================================================================

validate_categories() {
    for cat in "${SELECTED_CATEGORIES[@]}"; do
        local valid=false
        for valid_cat in "${VALID_CATEGORIES[@]}"; do
            if [[ "$cat" == "$valid_cat" ]]; then
                valid=true
                break
            fi
        done
        if [[ "$valid" == "false" ]]; then
            log_error "Unknown category: $cat"
            log_info "Valid categories: ${VALID_CATEGORIES[*]}"
            exit 1
        fi
    done
}

list_rules_in_category() {
    local rules_dir="$1"
    local category="$2"

    [[ ! -d "$rules_dir/$category" ]] && return

    find "$rules_dir/$category" -name "*.md" -type f | while read -r file; do
        echo "$category/$(basename "$file")"
    done
}

# ============================================================================
# Rule Comparison
# ============================================================================

compare_rule() {
    local rule_path="$1"      # e.g., "core/workflow.md"
    local source_dir="$2"
    local target_dir="$3"

    local source_file="$source_dir/$rule_path"
    local target_file="$target_dir/$rule_path"

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

sync_rules() {
    local mode="$1"
    local target_path="$2"

    # Resolve paths
    TARGET_PATH=$(cd "$target_path" && pwd)
    local source_dir target_dir

    if [[ "$mode" == "pull" ]]; then
        log_section "📥 Pulling rules from $TARGET_PATH"
        source_dir="$TARGET_PATH/.claude/rules"
        target_dir="$CURRENT_RULES_DIR"
    else
        log_section "📤 Pushing rules to $TARGET_PATH"
        source_dir="$CURRENT_RULES_DIR"
        target_dir="$TARGET_PATH/.claude/rules"
    fi

    # Validate paths
    if [[ ! -d "$source_dir" ]]; then
        log_error "Source rules directory not found: $source_dir"
        exit 1
    fi

    if [[ ! -d "$target_dir" ]] && [[ "$DRY_RUN" == "false" ]]; then
        log_warning "Target rules directory not found: $target_dir"
        log_info "Creating directory..."
        mkdir -p "$target_dir"
    fi

    # Determine categories to sync
    local categories_to_sync
    if [[ ${#SELECTED_CATEGORIES[@]} -gt 0 ]]; then
        validate_categories
        categories_to_sync=("${SELECTED_CATEGORIES[@]}")
        log_info "Selected categories: ${categories_to_sync[*]}"
    else
        # All categories
        categories_to_sync=("${VALID_CATEGORIES[@]}")
        log_info "Syncing all categories"
    fi

    # Collect all rules to check
    echo ""
    log_info "Scanning rules..."

    declare -a all_rules
    for category in "${categories_to_sync[@]}"; do
        while IFS= read -r rule; do
            all_rules+=("$rule")
        done < <(list_rules_in_category "$source_dir" "$category")
    done

    if [[ ${#all_rules[@]} -eq 0 ]]; then
        log_warning "No rules found in source"
        exit 0
    fi

    log_success "Found ${#all_rules[@]} rules in source"

    # Analyze rules by category
    echo ""
    log_info "Analyzing rules..."
    echo ""

    declare -A category_new category_updated category_same
    declare -A rule_status

    for category in "${categories_to_sync[@]}"; do
        category_new["$category"]=0
        category_updated["$category"]=0
        category_same["$category"]=0
    done

    local total_new=0 total_updated=0 total_same=0

    for rule in "${all_rules[@]}"; do
        local status=$(compare_rule "$rule" "$source_dir" "$target_dir")
        rule_status["$rule"]="$status"

        local category=$(dirname "$rule")

        case "$status" in
            NEW)
                ((category_new["$category"]++))
                ((total_new++))
                ;;
            NEWER)
                ((category_updated["$category"]++))
                ((total_updated++))
                ;;
            SAME)
                ((category_same["$category"]++))
                ((total_same++))
                ;;
        esac
    done

    # Display table
    echo "┌────────────────┬─────┬─────┬──────┐"
    echo "│ Category       │ New │ Upd │ Same │"
    echo "├────────────────┼─────┼─────┼──────┤"

    for category in "${categories_to_sync[@]}"; do
        printf "│ %-14s │ %3d │ %3d │ %4d │\n" \
            "$category" \
            "${category_new[$category]}" \
            "${category_updated[$category]}" \
            "${category_same[$category]}"
    done

    echo "└────────────────┴─────┴─────┴──────┘"
    echo ""

    # Summary
    log_section "Summary"
    echo "New rules: $total_new"
    echo "Updated rules: $total_updated"
    echo "Unchanged: $total_same"
    echo ""

    local total_to_sync=$((total_new + total_updated))
    if [[ $total_to_sync -eq 0 ]]; then
        log_success "All rules are up to date!"
        return 0
    fi

    # Dry run exit
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "🔍 DRY RUN MODE - No changes made"
        log_info "Run without --dry-run to apply changes"
        return 0
    fi

    # Confirm
    echo -n "Proceed with syncing $total_to_sync rules? (y/n) "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Cancelled by user"
        return 0
    fi

    # Copy rules
    echo ""
    log_info "Syncing rules..."
    echo ""

    for rule in "${all_rules[@]}"; do
        local status="${rule_status[$rule]}"
        if [[ "$status" == "NEW" ]] || [[ "$status" == "NEWER" ]]; then
            local source_file="$source_dir/$rule"
            local target_file="$target_dir/$rule"

            # Create directory if needed
            local target_category=$(dirname "$target_file")
            mkdir -p "$target_category"

            # Backup if exists (unless --force)
            if [[ -f "$target_file" ]] && [[ "$FORCE" == "false" ]]; then
                local backup_file="${target_file}.backup-$(date +%Y%m%d-%H%M%S)"
                cp "$target_file" "$backup_file"
            fi

            # Copy
            cp "$source_file" "$target_file"
            log_success "Synced: $rule"
        fi
    done

    echo ""
    log_success "Sync complete! Updated $total_to_sync rules"
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

    # Check current project has rules
    if [[ ! -d "$CURRENT_RULES_DIR" ]]; then
        log_error "Current project has no rules directory: $CURRENT_RULES_DIR"
        exit 1
    fi

    # Execute sync
    sync_rules "$MODE" "$TARGET_PATH"
}

main "$@"
