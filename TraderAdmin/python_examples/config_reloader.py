#!/usr/bin/env python3
"""
Example of configuration live-reload in Python.
This demonstrates how the orchestrator service can reload its configuration
without restarting when the config.toml file is updated.
"""

import signal
import sys
import threading
import time
from pathlib import Path

import tomli

# Configuration path
CONFIG_PATH = Path("/config/config.toml")
# Thread-safe lock for config access
config_lock = threading.Lock()
# Global configuration
config = {}


def load_config(path):
    """Load configuration from TOML file."""
    try:
        with open(path, "rb") as f:
            return tomli.load(f)
    except Exception as e:
        print(f"Error loading config from {path}: {e}")
        return {}


def reload_config(signum=None, frame=None):
    """Signal handler to reload configuration."""
    global config
    print("Reloading configuration...")

    with config_lock:
        new_config = load_config(CONFIG_PATH)
        if new_config:
            config.update(new_config)
            print("Configuration successfully reloaded")
        else:
            print("Failed to reload configuration, using previous configuration")


def print_config():
    """Print the current configuration (for demonstration)."""
    with config_lock:
        print("\nCurrent configuration:")
        print("=====================")
        if not config:
            print("No configuration loaded")
            return

        for section, values in config.items():
            print(f"[{section}]")
            if isinstance(values, dict):
                for key, value in values.items():
                    print(f"  {key} = {value}")
            else:
                print(f"  {values}")
            print()


def main():
    """Main function."""
    global config

    # Set up signal handler for SIGUSR1
    signal.signal(signal.SIGUSR1, reload_config)

    # Load initial configuration
    config = load_config(CONFIG_PATH)

    print(f"Configuration loaded from {CONFIG_PATH}")
    print("Send SIGUSR1 signal to reload configuration")
    print(f"For example: kill -SIGUSR1 {sys.getpid()}")

    print_config()

    # Main loop
    try:
        while True:
            # Do something with the configuration
            time.sleep(10)
            print(f"Process still running, PID: {sys.getpid()}")
    except KeyboardInterrupt:
        print("\nExiting gracefully")
        sys.exit(0)


if __name__ == "__main__":
    main()
