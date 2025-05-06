#!/usr/bin/env python
"""
Pre-commit hook to ensure files end with exactly one newline and have no trailing whitespace.
"""

import argparse
import sys


def fix_file_ending(filename):
    """Ensure file ends with exactly one newline and has no trailing whitespace."""
    try:
        with open(filename, "rb") as f:
            content = f.read()

        # Split into lines and process each one
        lines = content.split(b"\n")

        # Remove trailing whitespace from each line
        clean_lines = [line.rstrip() for line in lines]

        # Check for lines with trailing whitespace
        whitespace_lines = []
        for i, (original, clean) in enumerate(zip(lines, clean_lines)):
            if original != clean:
                whitespace_lines.append(i + 1)  # 1-indexed line numbers

        # Join lines back together with newlines
        content = b"\n".join(clean_lines)

        # Check if content already ends correctly (single newline)
        correct_ending = content.endswith(b"\n") and not content.endswith(b"\n\n")
        needs_ending_fix = not correct_ending

        # If no whitespace issues and ending is correct, no changes needed
        if not whitespace_lines and not needs_ending_fix:
            return False, [], correct_ending

        # Ensure the file ends with exactly one newline
        if content.endswith(b"\n"):
            # Remove all trailing newlines
            content = content.rstrip()

        # Add a single newline
        content = content + b"\n"

        # Write back to file
        with open(filename, "wb") as f:
            f.write(content)

        return True, whitespace_lines, correct_ending
    except Exception as e:
        print(f"Error processing {filename}: {e}", file=sys.stderr)
        return False, [], False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to fix")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    return_code = 0
    fixed_files = []

    for filename in args.filenames:
        fixed, whitespace_lines, correct_ending = fix_file_ending(filename)
        if fixed:
            fixed_files.append((filename, whitespace_lines, correct_ending))
            return_code = 1  # Indicate a file was modified

    if fixed_files:
        print(f"Fixed {len(fixed_files)} file(s):")
        for filename, whitespace_lines, correct_ending in fixed_files:
            print(f"  - {filename}")
            if args.verbose:
                if whitespace_lines:
                    print(
                        f"    * Fixed trailing whitespace on lines: {', '.join(str(l) for l in whitespace_lines)}"
                    )
                if not correct_ending:
                    print(f"    * Fixed file ending")

    return return_code


if __name__ == "__main__":
    sys.exit(main())
