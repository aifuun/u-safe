#!/usr/bin/env python3
"""Project Overview - Main Entry Point.

Orchestrates data collection, health calculation, and formatting.
Replaces overview.sh and status.sh per ADR-003.

Usage:
    # Terminal output (default)
    ./overview.py

    # HTML report
    ./overview.py --format=html

    # JSON output
    ./overview.py --format=json

    # Save to file
    ./overview.py --format=html --output=report.html

    # HTML without auto-opening browser
    ./overview.py --format=html --no-open

Example:
    >>> python overview.py --format=terminal
    📊 AI Dev Framework - Development Status
    ...
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add collectors and formatters to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from collectors import (
    git_collector,
    framework_collector,
    work_collector,
    pattern_detector,
    project_collector
)
from formatters import (
    health_calculator,
    terminal_formatter,
    html_formatter
)


def collect_all_data(project_root: str = '.') -> Dict[str, Any]:
    """
    Collect all project data from various sources.

    Args:
        project_root: Root directory of project (default: current dir)

    Returns:
        Dictionary with keys: git, framework, work, patterns, project, health

    Example:
        >>> data = collect_all_data()
        >>> print(f"Health: {data['health']['score']}/100")
    """
    print("📊 Collecting project data...", file=sys.stderr)

    # Collect from all sources
    git_data = git_collector.collect_git_status()
    framework_data = framework_collector.collect_framework_info()
    work_data = work_collector.collect_work_info()
    patterns = pattern_detector.detect_patterns()
    project_data = project_collector.collect_project_info(project_root)

    # Combine data
    combined_data = {
        'git': git_data,
        'framework': framework_data,
        'work': work_data,
        'patterns': patterns,
        'project': project_data
    }

    # Calculate health score
    health = health_calculator.calculate(combined_data)
    combined_data['health'] = health

    return combined_data


def get_project_name(project_root: str = '.') -> str:
    """
    Get project name from directory or package.json.

    Args:
        project_root: Root directory of project

    Returns:
        Project name string
    """
    # Try package.json first
    package_json = Path(project_root) / 'package.json'
    if package_json.exists():
        try:
            with open(package_json) as f:
                data = json.load(f)
                name = data.get('name', '')
                if name:
                    return name
        except (json.JSONDecodeError, IOError):
            pass

    # Fallback to directory name
    return Path(project_root).resolve().name


def format_output(data: Dict[str, Any], format_type: str, project_name: str,
                  auto_open: bool = True) -> str:
    """
    Format collected data for output.

    Args:
        data: Collected project data
        format_type: Output format ('terminal', 'html', 'json')
        project_name: Name of the project
        auto_open: Whether to auto-open HTML reports

    Returns:
        Formatted output string or file path

    Raises:
        ValueError: If format_type is invalid
    """
    if format_type == 'terminal':
        return terminal_formatter.format(data, project_name)

    elif format_type == 'html':
        # Returns file path
        return html_formatter.format(data, project_name, auto_open)

    elif format_type == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False)

    else:
        raise ValueError(f"Invalid format: {format_type}")


def main():
    """Main entry point for overview command."""
    parser = argparse.ArgumentParser(
        description='Generate project overview with health metrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Terminal output (default)
  %(prog)s --format=html            # Generate HTML report
  %(prog)s --format=json            # JSON output
  %(prog)s --format=html --no-open  # HTML without auto-opening
  %(prog)s --output=report.json     # Save JSON to file
        """
    )

    parser.add_argument(
        '--format',
        choices=['terminal', 'html', 'json'],
        default='terminal',
        help='Output format (default: terminal)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (optional, for html/json formats)'
    )

    parser.add_argument(
        '--no-open',
        action='store_true',
        help="Don't auto-open HTML reports in browser"
    )

    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    try:
        # Get project name
        project_name = get_project_name(args.project_root)

        # Collect data
        data = collect_all_data(args.project_root)

        # Format output
        auto_open = not args.no_open
        output = format_output(data, args.format, project_name, auto_open)

        # Handle output
        if args.format == 'html':
            # output is a file path
            if args.output:
                # Copy to specified location
                import shutil
                shutil.copy(output, args.output)
                print(f"✅ Report saved to: {args.output}", file=sys.stderr)
            else:
                print(f"✅ Report generated: {output}", file=sys.stderr)
        else:
            # output is content string
            if args.output:
                # Write to file
                Path(args.output).write_text(output, encoding='utf-8')
                print(f"✅ Output saved to: {args.output}", file=sys.stderr)
            else:
                # Print to stdout
                print(output)

        # Show health summary
        if args.format != 'json':
            health = data['health']
            score = health['score']
            grade = health['grade']
            print(f"\n✨ Health Score: {score}/100 (Grade: {grade})", file=sys.stderr)

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
