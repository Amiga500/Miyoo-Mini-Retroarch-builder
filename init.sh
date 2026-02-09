#!/bin/bash
set -euo pipefail

echo "Initializing submodules..."
git submodule init || { echo "Error: Failed to initialize submodules"; exit 1; }
git submodule update || { echo "Error: Failed to update submodules"; exit 1; }

echo "Applying buildbot tweaks patch..."
# Check if patch is already applied
if patch -p0 --dry-run --silent < ./buildbot-tweaks.patch 2>/dev/null; then
    echo "Applying patch..."
    patch -p0 < ./buildbot-tweaks.patch
    echo "Patch applied successfully"
elif patch -p0 -R --dry-run --silent < ./buildbot-tweaks.patch 2>/dev/null; then
    echo "Patch already applied, skipping"
else
    echo "ERROR: Patch cannot be applied cleanly"
    echo "This may indicate the libretro-super submodule has been modified"
    echo "or is at a different version than expected."
    exit 1
fi

echo "Initialization complete!"
