# Ensure src is in path and disable mypy
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path.resolve()))

def pytest_configure(config):
    """Disable mypy plugin if it's loaded."""
    plugins = getattr(config, "_plugins", {})
    for plugin_name in list(plugins):
        if "mypy" in plugin_name:
            plugins.pop(plugin_name, None)

    # Explicitly set PYTHONPATH for tests - use os.pathsep for cross-platform compatibility
    if "PYTHONPATH" not in os.environ:
        os.environ["PYTHONPATH"] = str(src_path.resolve())
    else:
        os.environ["PYTHONPATH"] = f"{str(src_path.resolve())}{os.pathsep}{os.environ['PYTHONPATH']}" 