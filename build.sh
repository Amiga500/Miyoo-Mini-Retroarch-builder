#!/bin/bash
set -euo pipefail

# Error handler
trap 'echo "Error on line $LINENO. Exiting."; exit 1' ERR

script_dir=$(cd -- "$(dirname "$0")" > /dev/null 2>&1 && pwd -P)
recipe_dir="$script_dir/$1"
build_name=$(basename "$1")
build_dir="$script_dir/build/$build_name"
recipe="$recipe_dir/libretro-cores"

# Detect CSV recipe and convert if needed
if [ -f "$recipe_dir/libretro-cores.csv" ]; then
    "$script_dir/csv2recipe.py" "$recipe_dir/libretro-cores.csv" "$recipe"
elif [ ! -f "$recipe" ]; then
    echo "Error: No valid recipe found in $recipe_dir"
    exit 1
fi

cd "$script_dir/libretro-super" || { echo "Error: Failed to cd to libretro-super. Did you run 'make init'?"; exit 1; }
./libretro-buildbot-recipe.sh "$recipe"

mkdir -p "$build_dir"

# Check if build produced any output
if [ ! -d "dist/unix" ]; then
    echo "Error: Build did not create dist/unix directory"
    exit 1
fi

cd dist/unix || { echo "Error: Failed to cd to dist/unix"; exit 1; }

# Check if any .so files were built
if ! ls ./*.so 1> /dev/null 2>&1; then
    echo "Warning: No .so files found in dist/unix - build may have failed"
fi

for i in *.so; do
    # Skip if glob didn't match any files
    [ -e "$i" ] || continue
    info_file="../info/${i%.*}.info"
    if [ -f "$info_file" ]; then
        cp "$info_file" "$build_dir"
    fi
done

ls -lah ./

cd "$script_dir" || { echo "Error: Failed to cd back to script directory"; exit 1; }
cp -arf libretro-super/dist/unix/. "$build_dir"

# Only remove recipe on successful completion
rm "$recipe"

echo "Build completed successfully!"
