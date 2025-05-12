"""
Simple test script to verify that imports from the src package work correctly.
If this script runs without errors, your environment is set up properly.
"""

# Try to import from various src subpackages
try:
    # Test importing from src.utils
    from src.utils.logger import log_info

    log_info("Successfully imported from src.utils")

    # Test importing from src.models
    from src.models.option import OptionSpread

    print("Successfully imported from src.models")

    # Test importing from src.app
    from src.app.config import Config

    print("Successfully imported from src.app")

    print("\nAll imports successful! Your environment is set up correctly.")

except ImportError as e:
    print(f"\nImport Error: {e}")
    print("\nYour environment may not be set up correctly.")
    print(
        "Please run the setup-dev.ps1 script to install the package in development mode:"
    )
    print("    ./setup-dev.ps1")

except Exception as e:
    print(f"\nUnexpected error: {e}")
    print("Please check your installation and try again.")
