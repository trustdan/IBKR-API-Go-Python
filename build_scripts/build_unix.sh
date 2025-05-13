#!/bin/bash
set -e

echo "Building TraderAdmin for Unix-like systems (Linux/macOS)..."

# Store script directory and move to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Determine the platform
PLATFORM=$(uname -s)
if [ "$PLATFORM" = "Darwin" ]; then
    echo "Building for macOS..."
    TARGET="darwin"
elif [ "$PLATFORM" = "Linux" ]; then
    echo "Building for Linux..."
    TARGET="linux"
else
    echo "Unsupported platform: $PLATFORM"
    exit 1
fi

# Build Wails application
echo "Building Wails application..."
wails build -platform $TARGET -trimpath -ldflags="-s -w"

# Check if build was successful
if [ ! -f "./build/bin/TraderAdmin" ] && [ ! -f "./build/bin/TraderAdmin.app" ]; then
    echo "ERROR: Wails build failed! TraderAdmin executable not found."
    exit 1
fi

# Create distribution archive
echo "Creating distribution archive..."
if [ "$TARGET" = "darwin" ]; then
    # For macOS, create a DMG if possible
    if command -v create-dmg &> /dev/null; then
        echo "Creating DMG for macOS..."
        create-dmg \
            --volname "TraderAdmin" \
            --volicon "./frontend/public/appicon.icns" \
            --window-pos 200 120 \
            --window-size 800 400 \
            --icon-size 100 \
            --icon "TraderAdmin.app" 200 190 \
            --hide-extension "TraderAdmin.app" \
            --app-drop-link 600 185 \
            "TraderAdmin.dmg" \
            "./build/bin/TraderAdmin.app"
    else
        # Fallback to zip if create-dmg is not available
        echo "create-dmg not found, creating zip archive instead..."
        (cd ./build/bin && zip -r ../../TraderAdmin-macos.zip TraderAdmin.app)
    fi
else
    # For Linux, create a tar.gz archive
    echo "Creating tar.gz archive for Linux..."
    (cd ./build/bin && tar -czf ../../TraderAdmin-linux.tar.gz TraderAdmin)
fi

echo "Build completed successfully!"
if [ "$TARGET" = "darwin" ]; then
    if [ -f "TraderAdmin.dmg" ]; then
        echo "Distribution created: TraderAdmin.dmg"
    else
        echo "Distribution created: TraderAdmin-macos.zip"
    fi
else
    echo "Distribution created: TraderAdmin-linux.tar.gz"
fi

exit 0
