#!/usr/bin/env python
"""
Analyze imports in the project to find potential circular references
or modules imported through multiple paths.
"""

import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple


def find_python_files(start_dir: str) -> List[str]:
    """Find all Python files in the given directory and subdirectories."""
    python_files = []
    for root, _, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def extract_imports(file_path: str) -> List[Tuple[str, str]]:
    """Extract import statements from a Python file."""
    imports = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find import statements
    import_pattern = r"^\s*from\s+([\w.]+)\s+import\s+(.+)$"
    for line in content.split("\n"):
        line = line.strip()

        # Skip comment lines
        if line.startswith("#"):
            continue

        # Check for from ... import ...
        match = re.match(import_pattern, line)
        if match:
            module_path, imported_items = match.groups()
            imports.append((module_path, imported_items))

    return imports


def analyze_imports():
    """Analyze import references across the project."""
    start_dir = "src"
    if not os.path.exists(start_dir):
        print(f"Error: Directory '{start_dir}' not found.")
        sys.exit(1)

    print(f"Finding Python files in '{start_dir}'...")
    python_files = find_python_files(start_dir)
    print(f"Found {len(python_files)} Python files.")

    # Keep track of module references
    references = defaultdict(set)

    # Analyze each file
    for file_path in python_files:
        # Create a module path from the file path
        rel_path = os.path.relpath(file_path)
        module_path = rel_path.replace(os.sep, ".").replace(".py", "")

        # Extract imports
        imports = extract_imports(file_path)

        # Record all module references
        for imported_module, _ in imports:
            if imported_module.startswith("."):
                # Handle relative imports - would need more complex handling
                continue

            # Map src.utils.logger -> utils/logger.py for detection
            if imported_module.startswith("src."):
                parts = imported_module.split(".")
                mapped_path = os.path.join(*parts[1:]) + ".py"
                references[mapped_path].add(rel_path)

    # Find modules referenced through multiple paths
    problematic_modules = {}
    for module_path, referencing_files in references.items():
        # Check if this module is also imported through another path
        for other_path, other_refs in references.items():
            if module_path != other_path and os.path.basename(
                module_path
            ) == os.path.basename(other_path):
                # Check if both modules exist
                if os.path.exists(module_path) and os.path.exists(other_path):
                    key = (module_path, other_path)
                    problematic_modules[key] = referencing_files.union(other_refs)

    # Report findings
    if problematic_modules:
        print("\nPotential problematic imports found:")
        for (path1, path2), refs in problematic_modules.items():
            print(f"\nModule imported through multiple paths:")
            print(f"  - {path1}")
            print(f"  - {path2}")
            print("Referenced by:")
            for ref in refs:
                print(f"  * {ref}")
    else:
        print("\nNo problematic imports found.")

    # Check for possible circular imports
    find_circular_imports()


def find_circular_imports():
    """Find potential circular imports in the project."""
    print("\nAnalyzing for circular imports...")
    circular_imports = []

    # Find all Python files
    python_files = find_python_files("src")

    # Build import map
    import_map = {}
    for file_path in python_files:
        # Get module name from file path
        rel_path = os.path.relpath(file_path)
        module_name = rel_path.replace(os.sep, ".").replace(".py", "")

        # Extract imports
        imports = extract_imports(file_path)
        imported_modules = []

        for imported_module, _ in imports:
            if imported_module.startswith("."):
                # Handle relative imports (simplistic approach)
                if imported_module == ".":
                    # from . import X
                    current_dir = os.path.dirname(rel_path)
                    imported_modules.append(current_dir.replace(os.sep, "."))
                elif imported_module.startswith(".."):
                    # from .. import X
                    dots = imported_module.count(".")
                    current_parts = module_name.split(".")
                    if len(current_parts) > dots:
                        parent_module = ".".join(current_parts[:-dots])
                        imported_modules.append(parent_module)
                else:
                    # from .submodule import X
                    current_dir = os.path.dirname(module_name)
                    submodule = imported_module[1:]  # Remove leading dot
                    imported_modules.append(f"{current_dir}.{submodule}")
            else:
                imported_modules.append(imported_module)

        import_map[module_name] = imported_modules

    # Check for circular imports
    for module, imports in import_map.items():
        for imported_module in imports:
            if imported_module in import_map and module in import_map.get(
                imported_module, []
            ):
                circular_imports.append((module, imported_module))

    # Report findings
    if circular_imports:
        print("\nPossible circular imports found:")
        for mod1, mod2 in circular_imports:
            print(f"  {mod1} <--> {mod2}")
    else:
        print("\nNo obvious circular imports found.")


if __name__ == "__main__":
    analyze_imports()

