#!/usr/bin/env python3
"""
Script to fix trailing whitespace and line ending issues in text files.
Works consistently across Windows, macOS, and Linux.
"""

import argparse
import fnmatch
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

# File extensions to process
TEXT_EXTENSIONS = {
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

# Directories to exclude
EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    "env",
    "__pycache__",
    "dist",
    "build",
    "bin",
    "obj",
    "target",
    "Debug",
    "Release",
}


def should_process_file(file_path: Path) -> bool:
    """Determine if a file should be processed based on extension and path."""
    # Check if the file extension is in our list
    if file_path.suffix.lower() not in TEXT_EXTENSIONS:
        return False

    # Check if the file is in an excluded directory
    path_parts = file_path.parts
    for part in path_parts:
        if part in EXCLUDE_DIRS:
            return False

    return True


def fix_file(file_path: Path, dry_run: bool = False) -> bool:
    """Fix trailing whitespace and line ending issues in a file.

    Returns True if file was modified, False otherwise.
    """
    try:
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()

        # Convert to string with universal newlines
        content_str = content.decode("utf-8", errors="replace")

        # Fix trailing whitespace
        fixed_content = re.sub(r"[ \t]+$", "", content_str, flags=re.MULTILINE)

        # Ensure consistent line endings (LF)
        fixed_content = fixed_content.replace("\r\n", "\n")

        # Ensure there's exactly one newline at the end
        fixed_content = fixed_content.rstrip("\n") + "\n"

        # Check if the file was modified
        modified = content_str != fixed_content

        if modified and not dry_run:
            # Write the fixed content back
            with open(file_path, "wb") as f:
                f.write(fixed_content.encode("utf-8"))

        return modified
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False


def process_directory(directory: Path, dry_run: bool = False) -> Dict[str, List[Path]]:
    """Process all appropriate files in a directory recursively.

    Returns a dictionary with lists of modified and examined files.
    """
    modified_files = []
    examined_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Skip excluded dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            file_path = Path(root) / file

            if should_process_file(file_path):
                examined_files.append(file_path)
                modified = fix_file(file_path, dry_run)
                if modified:
                    modified_files.append(file_path)

    return {"modified": modified_files, "examined": examined_files}


def main():
    parser = argparse.ArgumentParser(
        description="Fix whitespace and line ending issues."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=".",
        help="Directory to process (default: current directory)",
    )
    args = parser.parse_args()

    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"Error: {directory} is not a valid directory", file=sys.stderr)
        return 1

    results = process_directory(directory, args.dry_run)

    # Print results
    print(f"Examined {len(results['examined'])} files")
    print(
        f"{'Would modify' if args.dry_run else 'Modified'} {len(results['modified'])} files"
    )

    for file_path in results["modified"]:
        print(f"  {'Would fix' if args.dry_run else 'Fixed'}: {file_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
