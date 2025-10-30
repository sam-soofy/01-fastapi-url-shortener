#!/usr/bin/env python3
"""
Test runner script for the FastAPI URL Shortener application.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --verbose          # Run with verbose output
    python run_tests.py tests/test_auth.py # Run specific test file
"""

import argparse
import subprocess
import sys


def run_tests(args):
    """Run pytest with the specified arguments."""
    cmd = ["python", "-m", "pytest"]

    if args.coverage:
        cmd.extend(
            [
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-fail-under=80",
            ]
        )

    if args.verbose:
        cmd.append("-v")

    if args.test_files:
        cmd.extend(args.test_files)
    else:
        cmd.append("tests/")

    if args.markers:
        cmd.extend(["-m", args.markers])

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test runner for URL Shortener API")
    parser.add_argument(
        "--coverage", action="store_true", help="Run with coverage report"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Run with verbose output"
    )
    parser.add_argument("test_files", nargs="*", help="Specific test files to run")
    parser.add_argument("-m", "--markers", help="Pytest markers to filter tests")

    args = parser.parse_args()
    run_tests(args)


if __name__ == "__main__":
    main()
