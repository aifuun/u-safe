#!/usr/bin/env bash
# update-framework.sh - Sync entire framework between projects
# Part of AI Development Framework
# Orchestrates: update-pillars, update-rules, update-workflow, update-skills

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Components in sync order
ALL_COMPONENTS=("pillars" "rules" "workflow" "skills")

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

log_step() {
    echo ""
    echo -e "${MAGENTA}━━━ $* ━━━${NC}"
}

# ============================================================================
# Argument Parsing
# ============================================================================

MODE=""
TARGET_PATH=""
DRY_RUN=false
FORCE=false
SKIP_COMPONENTS=()
ONLY_COMPONENTS=()

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
            --skip)
                IFS=',' read -ra SKIP_COMPONENTS <<< "$2"
                shift 2
                ;;
            --only)
                IFS=',' read -ra ONLY_COMPONENTS <<< "$2"
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
Update Framework - Sync entire framework between projects

USAGE:
    update-framework.sh --from <project> [OPTIONS]
    update-framework.sh --to <project> [OPTIONS]

OPTIONS:
    --from <path>       Pull framework from source project
    --to <path>         Push framework to target project
    --dry-run           Preview changes without applying
    --force             Skip backup creation (overwrite directly)
    --skip <list>       Skip components (comma-separated)
    --only <list>       Only sync components (comma-separated)
    --help, -h          Show this help message

COMPONENTS:
    pillars, rules, workflow, skills

EXAMPLES:
    # Pull entire framework
    update-framework.sh --from ~/dev/ai-dev

    # Push entire framework
    update-framework.sh --to ~/projects/my-app

    # Preview update
    update-framework.sh --from ~/dev/ai-dev --dry-run

    # Only sync specific components
    update-framework.sh --from ~/dev/ai-dev --only rules,workflow

    # Skip specific components
    update-framework.sh --from ~/dev/ai-dev --skip skills
EOF
}

# ============================================================================
# Component Detection
# ============================================================================

get_components_to_sync() {
    # If --only specified, use only those
    if [[ ${#ONLY_COMPONENTS[@]} -gt 0 ]]; then
        echo "${ONLY_COMPONENTS[@]}"
        return
    fi

    # Otherwise, use all except --skip
    local components=()
    for component in "${ALL_COMPONENTS[@]}"; do
        local skip=false
        for skip_component in "${SKIP_COMPONENTS[@]}"; do
            if [[ "$component" == "$skip_component" ]]; then
                skip=true
                break
            fi
        done
        if [[ "$skip" == "false" ]]; then
            components+=("$component")
        fi
    done

    echo "${components[@]}"
}

validate_components() {
    local components=("$@")

    for component in "${components[@]}"; do
        local valid=false
        for valid_component in "${ALL_COMPONENTS[@]}"; do
            if [[ "$component" == "$valid_component" ]]; then
                valid=true
                break
            fi
        done
        if [[ "$valid" == "false" ]]; then
            log_error "Unknown component: $component"
            log_info "Valid components: ${ALL_COMPONENTS[*]}"
            exit 1
        fi
    done
}

# ============================================================================
# Component Sync
# ============================================================================

sync_component() {
    local component="$1"
    local mode="$2"
    local target_path="$3"
    local dry_run="$4"
    local force="$5"

    local script_name="update-${component}.sh"
    local script_path="$SKILLS_DIR/update-${component}/$script_name"

    # Check if script exists
    if [[ ! -f "$script_path" ]]; then
        log_error "Script not found: $script_path"
        return 1
    fi

    # Build command
    local cmd="$script_path"
    if [[ "$mode" == "pull" ]]; then
        cmd="$cmd --from $target_path"
    else
        cmd="$cmd --to $target_path"
    fi

    if [[ "$dry_run" == "true" ]]; then
        cmd="$cmd --dry-run"
    fi

    if [[ "$force" == "true" ]]; then
        cmd="$cmd --force"
    fi

    # Execute (with auto-confirm for non-dry-run)
    if [[ "$dry_run" == "false" ]]; then
        # Auto-confirm by piping 'y'
        echo "y" | bash "$cmd"
    else
        bash "$cmd"
    fi
}

# ============================================================================
# Analysis Phase
# ============================================================================

analyze_all_components() {
    local mode="$1"
    local target_path="$2"
    local components=("${@:3}")

    log_info "Analyzing components..."
    echo ""

    # Run each component in dry-run mode to get statistics
    declare -A component_new component_updated component_same

    for component in "${components[@]}"; do
        local script_name="update-${component}.sh"
        local script_path="$SKILLS_DIR/update-${component}/$script_name"

        if [[ ! -f "$script_path" ]]; then
            component_new["$component"]=0
            component_updated["$component"]=0
            component_same["$component"]=0
            continue
        fi

        # Run in dry-run mode and capture output
        local cmd="$script_path"
        if [[ "$mode" == "pull" ]]; then
            cmd="$cmd --from $target_path"
        else
            cmd="$cmd --to $target_path"
        fi
        cmd="$cmd --dry-run"

        local output=$(bash "$cmd" 2>&1 || true)

        # Parse output for statistics (look for "New: X, Updated: Y, Unchanged: Z")
        local new=$(echo "$output" | grep -oE "New [a-z]+: [0-9]+" | grep -oE "[0-9]+" | head -1 || echo "0")
        local updated=$(echo "$output" | grep -oE "Updated [a-z]+: [0-9]+" | grep -oE "[0-9]+" | head -1 || echo "0")
        local same=$(echo "$output" | grep -oE "Unchanged: [0-9]+" | grep -oE "[0-9]+" || echo "0")

        component_new["$component"]=${new:-0}
        component_updated["$component"]=${updated:-0}
        component_same["$component"]=${same:-0}
    done

    # Display table
    echo "┌────────────┬─────┬─────┬──────┬──────────┐"
    echo "│ Component  │ New │ Upd │ Same │ Action   │"
    echo "├────────────┼─────┼─────┼──────┼──────────┤"

    local total_new=0 total_updated=0 total_same=0

    for component in "${components[@]}"; do
        local new=${component_new[$component]:-0}
        local updated=${component_updated[$component]:-0}
        local same=${component_same[$component]:-0}
        local to_sync=$((new + updated))

        printf "│ %-10s │ %3d │ %3d │ %4d │" "$component" "$new" "$updated" "$same"

        if [[ $to_sync -gt 0 ]]; then
            printf " Update %-2d │\n" "$to_sync"
        else
            printf " %-9s │\n" "Skip"
        fi

        ((total_new += new))
        ((total_updated += updated))
        ((total_same += same))
    done

    echo "└────────────┴─────┴─────┴──────┴──────────┘"
    echo ""

    # Summary
    echo "📊 Overall Summary:"
    echo "- New items: $total_new"
    echo "- Updated items: $total_updated"
    echo "- Unchanged: $total_same"
    echo "- Total to sync: $((total_new + total_updated)) items"
    echo ""

    # Return total to sync
    echo "$((total_new + total_updated))"
}

# ============================================================================
# Main Sync Logic
# ============================================================================

sync_framework() {
    local mode="$1"
    local target_path="$2"

    # Resolve paths
    TARGET_PATH=$(cd "$target_path" && pwd)

    # Header
    if [[ "$mode" == "pull" ]]; then
        log_section "📥 Framework Sync: Pulling from $TARGET_PATH"
    else
        log_section "📤 Framework Sync: Pushing to $TARGET_PATH"
    fi

    # Get components to sync
    local components=($(get_components_to_sync))
    validate_components "${components[@]}"

    # Show selection if partial
    if [[ ${#ONLY_COMPONENTS[@]} -gt 0 ]]; then
        log_info "Only syncing: ${components[*]}"
        local skipped=()
        for component in "${ALL_COMPONENTS[@]}"; do
            if [[ ! " ${components[*]} " =~ " ${component} " ]]; then
                skipped+=("$component")
            fi
        done
        if [[ ${#skipped[@]} -gt 0 ]]; then
            log_info "Skipping: ${skipped[*]}"
        fi
    elif [[ ${#SKIP_COMPONENTS[@]} -gt 0 ]]; then
        log_info "Skipping: ${SKIP_COMPONENTS[*]}"
        log_info "Syncing: ${components[*]}"
    fi

    # Analysis phase
    echo ""
    local total_to_sync=$(analyze_all_components "$mode" "$TARGET_PATH" "${components[@]}")

    # Check if anything to sync
    if [[ $total_to_sync -eq 0 ]]; then
        log_success "All framework components are up to date!"
        return 0
    fi

    # Dry run exit
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "🔍 DRY RUN MODE - No changes made"
        log_info "Run without --dry-run to apply changes"
        return 0
    fi

    # Confirm
    echo -n "Proceed with framework sync? (y/n) "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Cancelled by user"
        return 0
    fi

    # Sync each component
    echo ""
    local step=1
    local total_steps=${#components[@]}
    local success_count=0
    local fail_count=0
    declare -a failed_components

    for component in "${components[@]}"; do
        log_step "Step $step/$total_steps: Syncing $component"

        if sync_component "$component" "$mode" "$TARGET_PATH" "false" "$FORCE"; then
            ((success_count++))
        else
            log_error "Failed to sync $component"
            ((fail_count++))
            failed_components+=("$component")
        fi

        ((step++))
    done

    # Final summary
    echo ""
    if [[ $fail_count -eq 0 ]]; then
        log_section "✅ Framework sync complete!"
        log_success "All $success_count components synced successfully"
    else
        log_section "⚠️  Framework sync completed with warnings"
        log_success "Successful: $success_count/$total_steps components"
        log_error "Failed: $fail_count components (${failed_components[*]})"
    fi

    return 0
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

    # Check mutually exclusive options
    if [[ ${#SKIP_COMPONENTS[@]} -gt 0 ]] && [[ ${#ONLY_COMPONENTS[@]} -gt 0 ]]; then
        log_error "Cannot use both --skip and --only"
        exit 1
    fi

    # Execute sync
    sync_framework "$MODE" "$TARGET_PATH"
}

main "$@"
