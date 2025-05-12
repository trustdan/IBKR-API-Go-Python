#!/usr/bin/env python
"""
Fix import statements in all Python files from relative to absolute.
This script walks through all Python files in the src directory and
replaces relative imports with absolute imports.
"""

import os
import re
import sys
from typing import List, Tuple


def find_python_files(start_dir: str) -> List[str]:
    """Find all Python files in the given directory and subdirectories."""
    python_files = []
    for root, _, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def fix_imports(file_path: str) -> Tuple[int, List[str]]:
    """Fix imports in a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find relative imports in the file
    relative_import_pattern = r"from\s+\.\.?[.\w]*\s+import"
    matches = re.findall(relative_import_pattern, content)

    if not matches:
        return 0, []

    fixed_imports = []

    # Process the file line by line
    lines = content.split("\n")
    updated_lines = []

    for line in lines:
        # Skip comment lines
        if line.strip().startswith("#"):
            updated_lines.append(line)
            continue

        # Look for relative imports
        if re.match(r"from\s+\.\.", line):
            # Get the import module parts
            match = re.match(r"from\s+(\.\.+)(\w[.\w]*)?\s+import\s+([\w, ]+)", line)
            if match:
                dots, module_path, imports = match.groups()

                # Determine the path based on the file's location
                rel_path = os.path.dirname(file_path)
                src_idx = rel_path.find("src")

                if src_idx >= 0:
                    # Get the parts after 'src' in the path
                    parts = rel_path[src_idx:].split(os.sep)

                    # Count the number of dots to determine how many levels to go up
                    levels_up = len(dots)

                    # Calculate the new module path
                    if module_path:
                        # Go up levels_up from the current dir
                        current_parts = parts[1:-(levels_up)]
                        if current_parts:
                            new_path = f"src.{'.'.join(current_parts)}.{module_path}"
                        else:
                            new_path = f"src.{module_path}"
                    else:
                        # If no module_path was given, we're importing from parent directly
                        current_parts = parts[1 : -(levels_up - 1)]
                        if current_parts:
                            new_path = f"src.{'.'.join(current_parts)}"
                        else:
                            new_path = "src"

                    # Replace the relative import with absolute import
                    new_line = f"from {new_path} import {imports}"
                    updated_lines.append(new_line)
                    fixed_imports.append(f"{line} -> {new_line}")
                    continue

        # Replace single dot relative imports
        single_dot_match = re.match(r"from\s+\.\s*(\w+)?\s+import\s+([\w, ]+)", line)
        if single_dot_match:
            module, imports = single_dot_match.groups()

            # Determine the path based on the file's location
            rel_path = os.path.dirname(file_path)
            src_idx = rel_path.find("src")

            if src_idx >= 0:
                # Get the parts after 'src' in the path
                parts = rel_path[src_idx:].split(os.sep)

                if module:
                    new_path = f"src.{'.'.join(parts[1:])}.{module}"
                else:
                    new_path = f"src.{'.'.join(parts[1:])}"

                # Replace the relative import with absolute import
                new_line = f"from {new_path} import {imports}"
                updated_lines.append(new_line)
                fixed_imports.append(f"{line} -> {new_line}")
                continue

        # Keep line unchanged if no replacement needed
        updated_lines.append(line)

    # Write the changes back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines))

    return len(fixed_imports), fixed_imports


def main():
    """Main function."""
    if len(sys.argv) > 1:
        start_dir = sys.argv[1]
    else:
        start_dir = "src"

    if not os.path.exists(start_dir):
        print(f"Error: Directory '{start_dir}' not found.")
        sys.exit(1)

    print(f"Finding Python files in '{start_dir}'...")
    python_files = find_python_files(start_dir)
    print(f"Found {len(python_files)} Python files.")

    total_fixes = 0

    print("\nFixing imports...")
    for file_path in python_files:
        num_fixes, fixed_imports = fix_imports(file_path)
        if num_fixes > 0:
            print(f"\n{file_path}: {num_fixes} import(s) fixed")
            for fix in fixed_imports:
                print(f"  {fix}")
            total_fixes += num_fixes

    print(f"\nTotal imports fixed: {total_fixes}")

    if total_fixes > 0:
        print("\nYou may want to run your type checker again to verify the changes.")


if __name__ == "__main__":
    main()

