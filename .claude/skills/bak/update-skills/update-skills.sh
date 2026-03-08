#!/usr/bin/env bash
# update-skills.sh - Sync skills between projects bidirectionally
# Part of AI Development Framework

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CURRENT_SKILLS_DIR="$PROJECT_ROOT/.claude/skills"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# Utility Functions
# ============================================================================

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

# ============================================================================
# Argument Parsing
# ============================================================================

MODE=""           # "pull" or "push"
TARGET_PATH=""    # Source/target project path
DRY_RUN=false
SELECTED_SKILLS=()
SHOW_HELP=false

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
            --skills)
                IFS=',' read -ra SELECTED_SKILLS <<< "$2"
                shift 2
                ;;
            --help|-h)
                SHOW_HELP=true
                shift
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
Update Skills - Sync skills between projects

USAGE:
    update-skills.sh --from <project> [OPTIONS]
    update-skills.sh --to <project> [OPTIONS]

OPTIONS:
    --from <path>          Pull skills from another project
    --to <path>            Push skills to another project
    --dry-run              Preview changes without applying
    --skills <list>        Comma-separated list of skills to sync
    --help, -h             Show this help message

EXAMPLES:
    # Pull all skills from buffer2
    update-skills.sh --from ../buffer2

    # Preview pull without changes
    update-skills.sh --from ../buffer2 --dry-run

    # Pull specific skills
    update-skills.sh --from ../buffer2 --skills adr,status

    # Push skills to another project
    update-skills.sh --to ../buffer --skills create-issues

    # Push with preview
    update-skills.sh --to ../buffer --dry-run

For more information, see SKILL.md
EOF
}

# ============================================================================
# Path Resolution
# ============================================================================

resolve_target_path() {
    local path="$1"

    # Handle relative paths
    if [[ "$path" == /* ]]; then
        # Absolute path
        echo "$path"
    else
        # Relative path - resolve from current project root
        echo "$(cd "$PROJECT_ROOT" && cd "$path" && pwd)"
    fi
}

verify_skills_directory() {
    local path="$1"
    local skills_dir="$path/.claude/skills"

    if [[ ! -d "$skills_dir" ]]; then
        log_error "Skills directory not found: $skills_dir"
        echo ""
        echo "Please check:"
        echo "1. Path is correct"
        echo "2. Project has .claude/skills/ directory"
        echo "3. You have read permissions"
        return 1
    fi

    return 0
}

# ============================================================================
# Skill Enumeration
# ============================================================================

list_skills() {
    local skills_dir="$1"

    # Find all directories containing SKILL.md
    while IFS= read -r -d '' skill_dir; do
        if [[ -f "$skill_dir/SKILL.md" ]]; then
            skill_name=$(basename "$skill_dir")
            echo "$skill_name"
        fi
    done < <(find "$skills_dir" -maxdepth 1 -type d -print0) | sort
}

filter_skills() {
    # Filter skills based on selected list
    # Input: all_skills (via stdin), selected skills array
    # Output: filtered skills (via stdout)

    local -a all_skills_array=()
    while IFS= read -r skill; do
        all_skills_array+=("$skill")
    done

    # If no selection, output all
    if [[ ${#SELECTED_SKILLS[@]} -eq 0 ]]; then
        printf '%s\n' "${all_skills_array[@]}"
        return
    fi

    # Filter to selected skills
    for skill in "${all_skills_array[@]}"; do
        for sel in "${SELECTED_SKILLS[@]}"; do
            if [[ "$skill" == "$sel" ]]; then
                echo "$skill"
                break
            fi
        done
    done
}

# ============================================================================
# Skill Comparison
# ============================================================================

get_file_mtime() {
    local file="$1"

    # Try macOS stat first, then Linux stat
    if stat -f %m "$file" 2>/dev/null; then
        return
    elif stat -c %Y "$file" 2>/dev/null; then
        return
    else
        echo "0"
    fi
}

get_file_lines() {
    local file="$1"
    wc -l < "$file" | tr -d ' '
}

compare_skill() {
    local skill="$1"
    local source_dir="$2"
    local target_dir="$3"

    local source_file="$source_dir/$skill/SKILL.md"
    local target_file="$target_dir/$skill/SKILL.md"

    # Check if target exists
    if [[ ! -f "$target_file" ]]; then
        echo "NEW"
        return
    fi

    # Get modification times
    local source_mtime=$(get_file_mtime "$source_file")
    local target_mtime=$(get_file_mtime "$target_file")

    # Get line counts
    local source_lines=$(get_file_lines "$source_file")
    local target_lines=$(get_file_lines "$target_file")

    # Compare
    if [[ $source_mtime -gt $target_mtime ]]; then
        echo "NEWER"
    elif [[ $source_mtime -lt $target_mtime ]]; then
        echo "OLDER"
    elif [[ $source_lines -ne $target_lines ]]; then
        echo "CONFLICT"
    else
        echo "SAME"
    fi
}

# ============================================================================
# Analysis & Reporting
# ============================================================================

analyze_skills() {
    local -n skills=$1
    local source_dir="$2"
    local target_dir="$3"
    local -n results=$4  # associative array: skill -> status

    log_info "Analyzing skills..."

    for skill in "${skills[@]}"; do
        status=$(compare_skill "$skill" "$source_dir" "$target_dir")
        results["$skill"]="$status"
    done
}

print_analysis_table() {
    local -n skills=$1
    local -n results=$2
    local source_dir="$3"
    local target_dir="$4"

    echo ""
    echo "📊 Analysis:"
    echo "┌─────────────────────┬──────────┬────────────────────────────────┐"
    echo "│ Skill               │ Status   │ Action                         │"
    echo "├─────────────────────┼──────────┼────────────────────────────────┤"

    local new_count=0
    local updated_count=0
    local older_count=0
    local conflict_count=0
    local same_count=0
    local total_lines=0

    for skill in "${skills[@]}"; do
        local status="${results[$skill]}"
        local source_file="$source_dir/$skill/SKILL.md"
        local target_file="$target_dir/$skill/SKILL.md"
        local source_lines=$(get_file_lines "$source_file")

        case "$status" in
            NEW)
                printf "│ %-19s │ NEW      │ Copy (%d lines)%*s│\n" \
                    "$skill" "$source_lines" $((20 - ${#source_lines})) " "
                ((new_count++))
                ((total_lines += source_lines))
                ;;
            NEWER)
                local target_lines=$(get_file_lines "$target_file")
                printf "│ %-19s │ NEWER    │ Update (%d → %d lines)%*s│\n" \
                    "$skill" "$target_lines" "$source_lines" $((15 - ${#target_lines} - ${#source_lines})) " "
                ((updated_count++))
                ((total_lines += source_lines))
                ;;
            OLDER)
                local target_lines=$(get_file_lines "$target_file")
                printf "│ %-19s │ OLDER    │ Skip (target newer: %d lines)%*s│\n" \
                    "$skill" "$target_lines" $((10 - ${#target_lines})) " "
                ((older_count++))
                ;;
            CONFLICT)
                printf "│ %-19s │ CONFLICT │ Manual review needed           │\n" "$skill"
                ((conflict_count++))
                ;;
            SAME)
                printf "│ %-19s │ SAME     │ Skip                           │\n" "$skill"
                ((same_count++))
                ;;
        esac
    done

    echo "└─────────────────────┴──────────┴────────────────────────────────┘"
    echo ""
    echo "Summary:"
    echo "- New skills: $new_count"
    echo "- Updated skills: $updated_count"
    [[ $older_count -gt 0 ]] && echo "- Older (skipped): $older_count"
    [[ $conflict_count -gt 0 ]] && echo "- Conflicts: $conflict_count"
    echo "- Unchanged: $same_count"

    local to_copy=$((new_count + updated_count))
    if [[ $to_copy -gt 0 ]]; then
        echo "- Total to copy: $to_copy skills ($total_lines lines)"
    fi
    echo ""
}

# ============================================================================
# Skill Copying
# ============================================================================

copy_skill() {
    local skill="$1"
    local source_dir="$2"
    local target_dir="$3"

    local source_skill_dir="$source_dir/$skill"
    local target_skill_dir="$target_dir/$skill"

    # Backup if exists
    if [[ -d "$target_skill_dir" ]]; then
        local backup_dir="$target_dir/${skill}.backup-$(date +%Y-%m-%d-%H%M%S)"
        cp -r "$target_skill_dir" "$backup_dir"
        log_info "Backed up to: ${backup_dir/$PROJECT_ROOT\//}"
    fi

    # Copy entire skill directory
    mkdir -p "$target_dir"
    cp -r "$source_skill_dir" "$target_skill_dir"

    # Report
    local lines=$(get_file_lines "$target_skill_dir/SKILL.md")
    log_success "Copied: $skill ($lines lines)"
}

copy_skills() {
    local -n skills=$1
    local -n results=$2
    local source_dir="$3"
    local target_dir="$4"

    local copied_count=0
    local total_lines=0

    echo ""
    log_section "Copying Skills"

    for skill in "${skills[@]}"; do
        local status="${results[$skill]}"

        case "$status" in
            NEW|NEWER)
                copy_skill "$skill" "$source_dir" "$target_dir"
                ((copied_count++))
                local lines=$(get_file_lines "$target_dir/$skill/SKILL.md")
                ((total_lines += lines))
                ;;
            OLDER|CONFLICT)
                log_warning "Skipped: $skill (status: $status)"
                ;;
            SAME)
                # Skip silently
                ;;
        esac
    done

    echo ""
    log_section "Summary"
    echo "Total processed: $copied_count skills"
    echo "Total lines: $total_lines"
    echo ""
}

# ============================================================================
# Main Operations
# ============================================================================

pull_skills() {
    local source_path="$1"
    local source_skills_dir="$source_path/.claude/skills"

    if $DRY_RUN; then
        log_section "📥 DRY RUN: Pulling skills from ${source_path/$HOME/\~}"
    else
        log_section "📥 Pulling skills from ${source_path/$HOME/\~}"
    fi

    # Verify source
    if ! verify_skills_directory "$source_path"; then
        return 1
    fi

    # List skills in source
    declare -a source_skills=()
    list_skills "$source_skills_dir" source_skills

    if [[ ${#source_skills[@]} -eq 0 ]]; then
        log_error "No skills found in source project"
        return 1
    fi

    log_info "Found ${#source_skills[@]} skills in source"

    # Filter to selected skills
    declare -a filtered_skills=()
    filter_skills source_skills SELECTED_SKILLS filtered_skills

    if [[ ${#filtered_skills[@]} -eq 0 ]]; then
        log_error "No skills matched selection"
        return 1
    fi

    if [[ ${#SELECTED_SKILLS[@]} -gt 0 ]]; then
        log_info "Selected skills: ${filtered_skills[*]}"
    fi

    # Analyze skills
    declare -A analysis_results
    analyze_skills filtered_skills "$source_skills_dir" "$CURRENT_SKILLS_DIR" analysis_results

    # Print analysis
    print_analysis_table filtered_skills analysis_results "$source_skills_dir" "$CURRENT_SKILLS_DIR"

    # Check if any skills to copy
    local has_changes=false
    for skill in "${filtered_skills[@]}"; do
        status="${analysis_results[$skill]}"
        if [[ "$status" == "NEW" || "$status" == "NEWER" ]]; then
            has_changes=true
            break
        fi
    done

    if ! $has_changes; then
        log_success "All skills are up to date!"
        return 0
    fi

    # Dry run exits here
    if $DRY_RUN; then
        echo ""
        log_info "🔍 DRY RUN MODE - No changes made"
        echo "Run without --dry-run to apply changes"
        return 0
    fi

    # Confirm
    echo ""
    read -p "Proceed? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Operation cancelled"
        return 0
    fi

    # Copy skills
    copy_skills filtered_skills analysis_results "$source_skills_dir" "$CURRENT_SKILLS_DIR"

    log_success "Skills updated successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Review changes: git diff .claude/skills/"
    echo "2. Test skills: /help"
    echo "3. Commit if satisfied: git add .claude/skills/"
    echo ""
}

push_skills() {
    local target_path="$1"
    local target_skills_dir="$target_path/.claude/skills"

    if $DRY_RUN; then
        log_section "📤 DRY RUN: Pushing skills to ${target_path/$HOME/\~}"
    else
        log_section "📤 Pushing skills to ${target_path/$HOME/\~}"
    fi

    # Verify target
    if ! verify_skills_directory "$target_path"; then
        return 1
    fi

    # List skills in current project
    declare -a current_skills=()
    list_skills "$CURRENT_SKILLS_DIR" current_skills

    if [[ ${#current_skills[@]} -eq 0 ]]; then
        log_error "No skills found in current project"
        return 1
    fi

    log_info "Found ${#current_skills[@]} skills in current project"

    # Filter to selected skills
    declare -a filtered_skills=()
    filter_skills current_skills SELECTED_SKILLS filtered_skills

    if [[ ${#filtered_skills[@]} -eq 0 ]]; then
        log_error "No skills matched selection"
        return 1
    fi

    if [[ ${#SELECTED_SKILLS[@]} -gt 0 ]]; then
        log_info "Selected skills: ${filtered_skills[*]}"
    fi

    # Analyze skills
    declare -A analysis_results
    analyze_skills filtered_skills "$CURRENT_SKILLS_DIR" "$target_skills_dir" analysis_results

    # Print analysis
    print_analysis_table filtered_skills analysis_results "$CURRENT_SKILLS_DIR" "$target_skills_dir"

    # Check if any skills to copy
    local has_changes=false
    for skill in "${filtered_skills[@]}"; do
        status="${analysis_results[$skill]}"
        if [[ "$status" == "NEW" || "$status" == "NEWER" ]]; then
            has_changes=true
            break
        fi
    done

    if ! $has_changes; then
        log_success "All target skills are up to date!"
        return 0
    fi

    # Dry run exits here
    if $DRY_RUN; then
        echo ""
        log_info "🔍 DRY RUN MODE - No changes made"
        echo "Run without --dry-run to apply changes"
        return 0
    fi

    # Confirm
    echo ""
    log_warning "This will modify ${target_path/$HOME/\~}/.claude/skills/"
    echo ""
    read -p "Proceed? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Operation cancelled"
        return 0
    fi

    # Copy skills
    copy_skills filtered_skills analysis_results "$CURRENT_SKILLS_DIR" "$target_skills_dir"

    log_success "Skills pushed successfully!"
    echo ""
}

# ============================================================================
# Main Entry Point
# ============================================================================

main() {
    parse_args "$@"

    if $SHOW_HELP; then
        show_help
        exit 0
    fi

    # Validate arguments
    if [[ -z "$MODE" ]]; then
        log_error "Missing --from or --to argument"
        echo ""
        show_help
        exit 1
    fi

    if [[ -z "$TARGET_PATH" ]]; then
        log_error "Missing project path"
        exit 1
    fi

    # Resolve target path
    TARGET_PATH=$(resolve_target_path "$TARGET_PATH")

    if [[ ! -d "$TARGET_PATH" ]]; then
        log_error "Project not found: $TARGET_PATH"
        exit 1
    fi

    # Execute operation
    case "$MODE" in
        pull)
            pull_skills "$TARGET_PATH"
            ;;
        push)
            push_skills "$TARGET_PATH"
            ;;
        *)
            log_error "Invalid mode: $MODE"
            exit 1
            ;;
    esac
}

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
