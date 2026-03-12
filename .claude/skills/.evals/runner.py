#!/usr/bin/env python3
"""Skill evaluation runner following Anthropic's official evaluation format.

Usage:
    python runner.py <test-case-file>
    python runner.py --all                  # Run all test cases
    python runner.py --skill start-issue    # Run all tests for a skill

Example:
    python runner.py test-cases/start-issue/basic.json
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class EvalResult:
    """Result of a single evaluation run.

    Attributes:
        test_case: Name of the test case file
        passed: Whether the evaluation passed
        expected: List of expected behaviors
        actual: List of observed behaviors
        score: Numeric score 0-100 (optional)
        errors: List of error messages
    """
    test_case: str
    passed: bool
    expected: List[str]
    actual: List[str]
    score: Optional[int] = None
    errors: Optional[List[str]] = None


def load_test_case(file_path: Path) -> Dict[str, Any]:
    """Load a JSON test case file.

    Args:
        file_path: Path to test case JSON file

    Returns:
        Dictionary containing test case data

    Raises:
        FileNotFoundError: If test case file doesn't exist
        json.JSONDecodeError: If JSON is malformed

    Example:
        >>> test = load_test_case(Path("test-cases/start-issue/basic.json"))
        >>> print(test["skills"])
        ['start-issue']
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Test case not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_test_case(test_case: Dict[str, Any]) -> List[str]:
    """Validate test case follows Anthropic schema.

    Args:
        test_case: Test case dictionary

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = validate_test_case({"skills": ["test"]})
        >>> assert "query" in errors[0]
    """
    errors = []

    # Required fields
    if "skills" not in test_case:
        errors.append("Missing required field: 'skills'")
    elif not isinstance(test_case["skills"], list):
        errors.append("Field 'skills' must be a list")

    if "query" not in test_case:
        errors.append("Missing required field: 'query'")
    elif not isinstance(test_case["query"], str):
        errors.append("Field 'query' must be a string")

    if "expected_behavior" not in test_case:
        errors.append("Missing required field: 'expected_behavior'")
    elif not isinstance(test_case["expected_behavior"], list):
        errors.append("Field 'expected_behavior' must be a list")

    # Optional fields
    if "files" in test_case and not isinstance(test_case["files"], list):
        errors.append("Field 'files' must be a list")

    return errors


def run_evaluation(test_case: Dict[str, Any]) -> EvalResult:
    """Execute a single evaluation test case.

    Args:
        test_case: Test case dictionary following Anthropic schema

    Returns:
        EvalResult with pass/fail and details

    Example:
        >>> test = {"skills": ["start-issue"], "query": "start issue #1",
        ...         "expected_behavior": ["Creates branch"]}
        >>> result = run_evaluation(test)
        >>> print(result.passed)
        False  # Not implemented yet
    """
    # Phase 1: Basic structure - actual execution in Phase 2/3
    # For now, return skeleton result
    return EvalResult(
        test_case=test_case.get("name", "unnamed"),
        passed=False,
        expected=test_case.get("expected_behavior", []),
        actual=["[Not implemented yet - Phase 1 creates structure only]"],
        errors=["Eval execution not implemented in Phase 1"]
    )


def format_result(result: EvalResult) -> str:
    """Format evaluation result for human-readable output.

    Args:
        result: EvalResult to format

    Returns:
        Formatted string with pass/fail and details

    Example:
        >>> res = EvalResult("test", True, ["A"], ["A"])
        >>> print(format_result(res))
        ✅ PASS: test
    """
    status = "✅ PASS" if result.passed else "❌ FAIL"
    lines = [f"{status}: {result.test_case}", ""]

    if result.score is not None:
        lines.append(f"Score: {result.score}/100")

    lines.append("Expected behaviors:")
    for behavior in result.expected:
        lines.append(f"  - {behavior}")

    lines.append("\nActual behaviors:")
    for behavior in result.actual:
        lines.append(f"  - {behavior}")

    if result.errors:
        lines.append("\nErrors:")
        for error in result.errors:
            lines.append(f"  - {error}")

    return "\n".join(lines)


def main() -> int:
    """Main entry point for eval runner.

    Returns:
        Exit code (0 = all passed, 1 = some failed, 2 = error)

    Example:
        $ python runner.py test-cases/start-issue/basic.json
        ❌ FAIL: basic
        ...
    """
    parser = argparse.ArgumentParser(
        description="Run skill evaluations following Anthropic format"
    )
    parser.add_argument(
        "test_case",
        nargs="?",
        help="Path to test case JSON file"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all test cases"
    )
    parser.add_argument(
        "--skill",
        help="Run all test cases for a specific skill"
    )

    args = parser.parse_args()

    # Determine which test cases to run
    if args.all:
        print("❌ Error: --all not implemented yet (Phase 2)")
        return 2
    elif args.skill:
        print(f"❌ Error: --skill not implemented yet (Phase 2)")
        return 2
    elif not args.test_case:
        parser.print_help()
        return 2

    # Run single test case
    try:
        test_path = Path(args.test_case)
        test_case = load_test_case(test_path)

        # Validate
        errors = validate_test_case(test_case)
        if errors:
            print(f"❌ Invalid test case: {test_path}")
            for error in errors:
                print(f"  - {error}")
            return 2

        # Execute
        result = run_evaluation(test_case)

        # Display
        print(format_result(result))

        return 0 if result.passed else 1

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 2
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 2
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
