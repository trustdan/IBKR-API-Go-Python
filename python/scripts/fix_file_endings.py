#!/usr/bin/env python
"""
Pre-commit hook to ensure files end with exactly one newline.
"""

import argparse
import sys


def fix_file_ending(filename):
    """Ensure file ends with exactly one newline."""
    try:
        with open(filename, "rb") as f:
            content = f.read()

        # Check if content ends with a single newline already
        if content.endswith(b"\n") and not content.endswith(b"\n\n"):
            # File already has a single newline, no fix needed
            return False

        # Remove trailing whitespace and newlines
        content = content.rstrip()

        # Add single newline
        content = content + b"\n"

        # Write back to file
        with open(filename, "wb") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error processing {filename}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to fix")
    args = parser.parse_args()

    return_code = 0
    fixed_files = []

    for filename in args.filenames:
        fixed = fix_file_ending(filename)
        if fixed:
            fixed_files.append(filename)
            return_code = 1  # Indicate a file was modified

    if fixed_files:
        print(f"Fixed {len(fixed_files)} file(s):")
        for file in fixed_files:
            print(f"  - {file}")

    return return_code


if __name__ == "__main__":
    sys.exit(main())
