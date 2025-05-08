#!/usr/bin/env python
"""
Pre-commit hook to ensure files end with exactly one newline and have no trailing whitespace.
"""

import argparse
import re
import sys
from pathlib import Path


def fix_file_ending(filename):
    """Ensure file ends with exactly one newline and has no trailing whitespace."""
    try:
        file_path = Path(filename)

        # Skip binary files and certain extensions
        if not is_text_file(file_path):
            return False, [], True, []

        with open(filename, "rb") as f:
            content = f.read()

        try:
            # Try to decode as UTF-8
            content_str = content.decode("utf-8", errors="strict")
            encoding = "utf-8"
        except UnicodeDecodeError:
            # If UTF-8 fails, use latin-1 as fallback
            content_str = content.decode("latin-1")
            encoding = "latin-1"

        # Check if there are any carriage returns
        had_crlf = "\r\n" in content_str

        # Fix trailing whitespace
        fixed_content = re.sub(r"[ \t]+$", "", content_str, flags=re.MULTILINE)

        # Normalize line endings to LF
        fixed_content = fixed_content.replace("\r\n", "\n")

        # Ensure the file ends with exactly one newline
        fixed_content = fixed_content.rstrip("\n") + "\n"

        # Check if any changes were made
        modified = content_str != fixed_content

        # Determine what changed
        whitespace_lines = []
        line_ending_changes = []

        if modified:
            # Track which lines had whitespace removed
            original_lines = content_str.split("\n")
            fixed_lines = fixed_content.split("\n")

            # Only check up to the length of the shorter list
            min_length = min(len(original_lines), len(fixed_lines))

            for i in range(min_length):
                if (
                    original_lines[i].rstrip() == fixed_lines[i]
                    and original_lines[i] != fixed_lines[i]
                ):
                    whitespace_lines.append(i + 1)  # 1-indexed line numbers

            if had_crlf:
                line_ending_changes = ["CRLF -> LF"]

            # Write the changes back to the file
            with open(filename, "wb") as f:
                f.write(fixed_content.encode(encoding))

        return modified, whitespace_lines, not modified, line_ending_changes
    except Exception as e:
        print(f"Error processing {filename}: {e}", file=sys.stderr)
        return False, [], False, []


def is_text_file(file_path):
    """Check if a file is a text file based on extension."""
    # Common text file extensions
    text_extensions = {
        ".py",
        ".go",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".html",
        ".css",
        ".scss",
        ".md",
        ".txt",
        ".yml",
        ".yaml",
        ".json",
        ".toml",
        ".xml",
        ".sh",
        ".bat",
        ".ps1",
        ".nsi",
        ".sql",
        ".cfg",
        ".conf",
        ".ini",
    }

    # Common binary file extensions to skip
    binary_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".pdf",
        ".exe",
        ".dll",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
    }

    ext = file_path.suffix.lower()

    # Skip known binary files
    if ext in binary_extensions:
        return False

    # Process known text files
    if ext in text_extensions:
        return True

    # For unknown extensions, try to check if it's a text file
    try:
        with open(file_path, "rb") as f:
            content = f.read(1024)  # Read first 1KB

            # Check for null bytes which usually indicate binary files
            if b"\x00" in content:
                return False

            # Try to decode as UTF-8
            try:
                content.decode("utf-8")
                return True
            except UnicodeDecodeError:
                pass

            # As a fallback, check if most characters are printable ASCII
            printable_chars = sum(32 <= byte <= 126 for byte in content)
            return printable_chars / len(content) > 0.8 if content else True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to fix")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    return_code = 0
    fixed_files = []
    skipped_files = []

    for filename in args.filenames:
        fixed, whitespace_lines, was_correct, line_ending_changes = fix_file_ending(
            filename
        )

        if not was_correct:
            if fixed:
                fixed_files.append((filename, whitespace_lines, line_ending_changes))
                return_code = 1  # Indicate a file was modified
            else:
                skipped_files.append(filename)

    # Group files by directory for cleaner output
    if fixed_files:
        # Group files by directories
        by_directory = {}
        for filename, whitespace_lines, line_ending_changes in fixed_files:
            path = Path(filename)
            parent = str(path.parent)
            if parent not in by_directory:
                by_directory[parent] = []
            by_directory[parent].append(
                (path.name, whitespace_lines, line_ending_changes)
            )

        print(f"Fixed {len(fixed_files)} file(s):")
        for directory, files in by_directory.items():
            print(f"  {directory}:")
            for file_name, whitespace_lines, line_ending_changes in files:
                changes = []
                if whitespace_lines:
                    changes.append("whitespace")
                if line_ending_changes:
                    changes.append("line endings")

                change_str = f" ({', '.join(changes)})" if changes else ""
                print(f"    - {file_name}{change_str}")

                if args.verbose:
                    if whitespace_lines:
                        if len(whitespace_lines) > 10:
                            # Just show count if too many lines
                            print(
                                f"      * Fixed trailing whitespace on {len(whitespace_lines)} lines"
                            )
                        else:
                            # Show specific lines if there are few
                            print(
                                f"      * Fixed trailing whitespace on lines: {', '.join(str(l) for l in whitespace_lines)}"
                            )
                    if line_ending_changes:
                        print(
                            f"      * Fixed line endings: {', '.join(line_ending_changes)}"
                        )

    return return_code


if __name__ == "__main__":
    sys.exit(main())
