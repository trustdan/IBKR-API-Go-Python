#!/usr/bin/env python3
"""
Convert YAML configuration to TOML format.
This ensures a consistent format for both Python and Go services.
"""

import argparse
import os
import sys
from pathlib import Path

import toml
import yaml


def convert_yaml_to_toml(yaml_file, toml_file):
    """Convert a YAML file to TOML format."""
    try:
        with open(yaml_file, "r") as f:
            yaml_data = yaml.safe_load(f)

        with open(toml_file, "w") as f:
            toml.dump(yaml_data, f)

        print(f"Successfully converted {yaml_file} to {toml_file}")
        return True
    except Exception as e:
        print(f"Error converting {yaml_file} to {toml_file}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convert YAML configuration to TOML format"
    )
    parser.add_argument("yaml_file", help="Path to the YAML file to convert")
    parser.add_argument(
        "--output",
        "-o",
        help="Path to the output TOML file (default: same name as input with .toml extension)",
    )

    args = parser.parse_args()

    yaml_path = Path(args.yaml_file)
    if not yaml_path.exists():
        print(f"Error: {yaml_path} does not exist", file=sys.stderr)
        return 1

    toml_path = Path(args.output) if args.output else yaml_path.with_suffix(".toml")

    if convert_yaml_to_toml(yaml_path, toml_path):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
