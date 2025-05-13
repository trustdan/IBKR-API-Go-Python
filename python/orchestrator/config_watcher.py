import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict

import toml
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ConfigWatcher")


class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, config_path: str, callback: Callable[[Dict[str, Any]], None]):
        super().__init__()
        self.config_path = Path(config_path)
        self.callback = callback
        self._last_modified = 0
        # Load initial config
        self.reload_config()

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent):
            return

        # Check if this is the config file we're watching
        if Path(event.src_path).resolve() == self.config_path.resolve():
            # Add a small delay to ensure file is completely written
            time.sleep(0.1)

            # Avoid duplicate events
            current_time = time.time()
            if current_time - self._last_modified > 1:  # Ignore events within 1 second
                self._last_modified = current_time
                logger.info(f"Config file changed: {event.src_path}")
                self.reload_config()

    def reload_config(self):
        try:
            if not self.config_path.exists():
                logger.error(f"Config file not found: {self.config_path}")
                return

            config = toml.load(self.config_path)
            logger.info(f"Config loaded successfully from {self.config_path}")

            # Call the callback with the new config
            self.callback(config)
        except Exception as e:
            logger.error(f"Error loading config: {e}")


class ConfigWatcher:
    def __init__(self, config_path: str, callback: Callable[[Dict[str, Any]], None]):
        self.config_path = Path(config_path)
        self.callback = callback
        self.observer = None
        self.event_handler = None

    def start(self):
        """Start watching the config file for changes"""
        if self.observer:
            logger.warning("Watcher already running")
            return

        config_dir = self.config_path.parent

        # Ensure directory exists
        if not config_dir.exists():
            logger.error(f"Config directory does not exist: {config_dir}")
            return

        self.event_handler = ConfigFileHandler(self.config_path, self.callback)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, str(config_dir), recursive=False)
        self.observer.start()
        logger.info(f"Started watching for changes to {self.config_path}")

    def stop(self):
        """Stop watching the config file"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped watching for config changes")
            self.observer = None


def config_changed_callback(config: Dict[str, Any]):
    """Example callback function that will be called when config changes"""
    logger.info("Config changed! New values:")

    # Log some key config values as an example
    if "general" in config:
        logger.info(f"Log level: {config['general'].get('log_level', 'not set')}")

    if "ibkr_connection" in config:
        conn = config["ibkr_connection"]
        logger.info(
            f"IBKR Connection: {conn.get('host', 'localhost')}:{conn.get('port', 'not set')}"
        )

    # Here you would update your application's runtime configuration
    # For example, adjust log levels, reconnect to services, etc.


def main():
    """Example main function to demonstrate usage"""
    # Get config path from environment or use default
    config_path = os.environ.get("CONFIG_PATH", "/app/config/config.toml")

    # Create a config watcher
    watcher = ConfigWatcher(config_path, config_changed_callback)

    try:
        # Start watching for changes
        watcher.start()

        # In a real application, you would do your main work here
        # This is just a placeholder to keep the script running
        logger.info("Application running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        watcher.stop()


if __name__ == "__main__":
    main()
