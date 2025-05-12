#!/usr/bin/env python
"""
Pre-commit hook to ensure files end with exactly one newline and have no trailing whitespace.
Normalizes all line endings to LF.
"""

import argparse
import os
import sys
from pathlib import Path


def is_binary(filename):
    """Check if file is binary."""
    try:
        with open(filename, "rb") as f:
            # Read 8000 bytes to determine if file is binary
            chunk = f.read(8000)
            # If there's a null byte, it's likely binary
            if b"\x00" in chunk:
                return True
            # Less than 10% of the characters are ASCII control chars (excluding tabs, newlines)
            control_chars = sum(1 for c in chunk if c < 9 or 10 < c < 32 or c == 127)
            return control_chars > len(chunk) * 0.1
    except (IOError, UnicodeDecodeError):
        return True


def fix_file_ending(filename):
    """Ensure file ends with exactly one newline, has no trailing whitespace, and uses LF line endings."""
    try:
        # Skip binary files
        if is_binary(filename):
            if os.environ.get("VERBOSE") == "1":
                print(f"Skipping binary file: {filename}")
            return False, [], True

        with open(filename, "rb") as f:
            content = f.read()

        # Convert CRLF to LF
        if b"\r\n" in content:
            content = content.replace(b"\r\n", b"\n")

        # Split into lines and process each one
        lines = content.split(b"\n")

        # Remove trailing whitespace from each line
        clean_lines = [line.rstrip() for line in lines]

        # Check for lines with trailing whitespace
        whitespace_lines = []
        for i, (original, clean) in enumerate(zip(lines, clean_lines)):
            if original != clean:
                whitespace_lines.append(i + 1)  # 1-indexed line numbers

        # Join lines back together with LF
        content = b"\n".join(clean_lines)

        # Check if content already ends correctly (single newline)
        correct_ending = content.endswith(b"\n") and not content.endswith(b"\n\n")
        needs_ending_fix = not correct_ending

        # If no whitespace issues and ending is correct, no changes needed
        if not whitespace_lines and not needs_ending_fix and b"\r\n" not in content:
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

    if args.verbose:
        os.environ["VERBOSE"] = "1"

    return_code = 0
    fixed_files = []
    groups = {}

    for filename in args.filenames:
        fixed, whitespace_lines, correct_ending = fix_file_ending(filename)
        if fixed:
            # Group by directory for cleaner output
            directory = str(Path(filename).parent)
            if directory not in groups:
                groups[directory] = []
            groups[directory].append((filename, whitespace_lines, correct_ending))
            return_code = 1  # Indicate a file was modified

    if groups:
        total_count = sum(len(files) for files in groups.values())
        print(f"Fixed {total_count} file(s):")

        for directory, files in sorted(groups.items()):
            print(f"  {directory}:")
            for filename, whitespace_lines, correct_ending in files:
                base_filename = os.path.basename(filename)
                print(f"  - {base_filename}")
                if args.verbose:
                    if whitespace_lines:
                        print(
                            f"    * Fixed trailing whitespace on lines: {', '.join(str(l) for l in whitespace_lines[:5])}"
                            + ("..." if len(whitespace_lines) > 5 else "")
                        )
                    if not correct_ending:
                        print(f"    * Fixed file ending")

    return return_code


if __name__ == "__main__":
    sys.exit(main())
