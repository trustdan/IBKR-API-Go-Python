#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# File extensions to process
TEXT_EXTENSIONS = {
    ".py",
    ".go",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".svelte",
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
    ".gitignore",
    ".gitattributes",
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


def should_process_file(file_path):
    """Determine if a file should be processed based on extension and path."""
    path_parts = Path(file_path).parts

    # Check if file is in an excluded directory
    for part in path_parts:
        if part in EXCLUDE_DIRS:
            return False

    # Check extension
    ext = Path(file_path).suffix.lower()
    if ext in TEXT_EXTENSIONS:
        return True

    # Check for files without extension that might be text
    if ext == "":
        name = Path(file_path).name.lower()
        if name in {"makefile", "dockerfile", "license", "readme"}:
            return True

    return False


def fix_file(file_path):
    """Fix line endings and trailing whitespace in a file."""
    try:
        # Read the file in binary mode to handle all line endings
        with open(file_path, "rb") as f:
            content = f.read()

        # Try to detect if file is binary
        if b"\x00" in content:
            print(f"Skipping binary file: {file_path}")
            return False

        # Decode as UTF-8
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            print(f"Warning: {file_path} is not UTF-8 encoded, skipping")
            return False

        # Normalize line endings to LF
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove trailing whitespace and ensure single newline at end
        lines = [line.rstrip() for line in text.split("\n")]
        new_text = "\n".join(lines).rstrip() + "\n"

        # Only write if content has changed
        if new_text.encode("utf-8") != content:
            # Write with LF line endings
            with open(file_path, "wb") as f:
                f.write(new_text.encode("utf-8"))
            print(f"Fixed: {file_path}")
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False


def main():
    modified_count = 0
    examined_count = 0

    # Walk through all files in the repository
    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            file_path = os.path.join(root, file)
            if should_process_file(file_path):
                examined_count += 1
                if fix_file(file_path):
                    modified_count += 1

    print(f"\nExamined {examined_count} files")
    print(f"Modified {modified_count} files")


if __name__ == "__main__":
    main()
