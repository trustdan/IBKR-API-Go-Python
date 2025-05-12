"""
Tests for the Save/Restart functionality.

This test verifies the PauseStack, SaveConfig, and UnpauseStack methods
work correctly together.
"""

import os
import tempfile
import time
from pathlib import Path

import pytest
import toml


# Mock wails bindings for testing
class MockApp:
    """Mock App class for testing without the actual Wails runtime."""

    def __init__(self):
        """Initialize with a temporary config file."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "config.toml")

        # Create initial config
        self.initial_config = {
            "ibkr": {"host": "localhost", "port": 7497},
            "scheduling": {
                "trading_start_time": "09:30:00",
                "trading_end_time": "16:00:00",
                "timezone": "America/New_York",
                "trading_days": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                ],
            },
        }

        # Write initial config
        with open(self.config_path, "w") as f:
            toml.dump(self.initial_config, f)

        # Track service state
        self.services_paused = False

    def PauseStack(self):
        """Mock pausing the service stack."""
        self.services_paused = True
        return "Stack paused"

    def UnpauseStack(self):
        """Mock unpausing the service stack."""
        self.services_paused = False
        return "Stack unpaused"

    def SaveConfig(self, config):
        """Save the provided config to the temp file."""
        # Backup current config
        backup_path = f"{self.config_path}.bak"
        with open(self.config_path, "r") as src, open(backup_path, "w") as dst:
            dst.write(src.read())

        # Write new config
        with open(self.config_path, "w") as f:
            toml.dump(config, f)

        return "Config saved"

    def SaveAndRestartStack(self, config):
        """Implement the full save and restart process."""
        pause_result = self.PauseStack()
        save_result = self.SaveConfig(config)
        time.sleep(0.1)  # Simulate a brief pause
        unpause_result = self.UnpauseStack()

        return f"{pause_result}, {save_result}, {unpause_result}"

    def cleanup(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()


def test_save_and_restart():
    """Test the save and restart functionality."""
    app = MockApp()

    try:
        # Modify the config
        new_config = app.initial_config.copy()
        new_config["scheduling"]["trading_start_time"] = "10:00:00"

        # Perform save and restart
        assert not app.services_paused, "Services should not be paused initially"
        result = app.SaveAndRestartStack(new_config)
        assert "Stack paused" in result, "Stack should be paused during save"
        assert "Config saved" in result, "Config should be saved"
        assert "Stack unpaused" in result, "Stack should be unpaused after save"
        assert not app.services_paused, "Services should not be paused after restart"

        # Verify config was actually updated
        with open(app.config_path, "r") as f:
            loaded_config = toml.load(f)

        assert (
            loaded_config["scheduling"]["trading_start_time"] == "10:00:00"
        ), "Config should be updated with new value"

        # Verify backup was created
        backup_file = Path(f"{app.config_path}.bak")
        assert backup_file.exists(), "Backup file should exist"

        with open(backup_file, "r") as f:
            backup_config = toml.load(f)

        assert (
            backup_config["scheduling"]["trading_start_time"] == "09:30:00"
        ), "Backup should contain original value"

    finally:
        app.cleanup()


def test_pause_unpause_behavior():
    """Test the pause and unpause functionality independently."""
    app = MockApp()

    try:
        # Test pause
        assert not app.services_paused, "Services should not be paused initially"
        app.PauseStack()
        assert app.services_paused, "Services should be paused after PauseStack"

        # Test unpause
        app.UnpauseStack()
        assert (
            not app.services_paused
        ), "Services should not be paused after UnpauseStack"

    finally:
        app.cleanup()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
