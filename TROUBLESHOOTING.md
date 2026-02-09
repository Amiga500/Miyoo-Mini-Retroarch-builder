# Troubleshooting Guide

## Common Issues and Solutions

### 1. "patch: **** malformed patch" when running make init

**Problem:** The buildbot-tweaks.patch file cannot be applied.

**Possible causes:**
- Git line ending conversion corrupted the patch
- libretro-super submodule is at wrong commit
- Patch was already applied

**Solutions:**

```bash
# Check if patch already applied
cd libretro-super
patch -p0 -R --dry-run --silent < ../buildbot-tweaks.patch
# If this succeeds, patch is already applied

# If patch was already applied:
cd ..
# Just continue, init.sh now handles this

# If submodule at wrong commit:
git submodule update --init --recursive

# If patch still fails:
# Reset submodule and try again
make reset-submodules
make init
```

### 2. "Docker: command not found"

**Problem:** Docker is not installed or not in PATH.

**Solutions:**

```bash
# Install Docker (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install docker.io

# Install Docker (macOS)
# Download Docker Desktop from docker.com

# Install Docker (Arch Linux)
sudo pacman -S docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in for group to take effect
```

### 3. "Permission denied" when running Docker

**Problem:** User doesn't have permission to access Docker socket.

**Solutions:**

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Test:
docker ps

# Alternative: Run with sudo (not recommended)
sudo make build/linux-armv7-neon
```

### 4. "Error: Failed to cd to libretro-super"

**Problem:** libretro-super submodule not initialized.

**Solution:**

```bash
# Initialize submodules
make init

# If that fails, manually:
git submodule init
git submodule update
```

### 5. "No .so files found in dist/unix"

**Problem:** Build completed but produced no output.

**Possible causes:**
- All cores failed to compile
- CSV recipe has no cores with `enabled=YES`
- Build errors were ignored

**Debugging:**

```bash
# Check build logs in terminal output
# Look for compilation errors

# Check CSV file
cat config/<target>/libretro-cores.csv
# Ensure at least one core has enabled=YES

# Try building single core
# Edit CSV to only include one core
# Run build again and check output carefully

# Check recipe was created
ls config/<target>/libretro-cores
# Should exist during build

# Check libretro-super/dist/unix after failed build
docker run -v .:/root/workspace ${DOCKER_IMAGE} \
    /bin/bash -c "ls -la /root/workspace/libretro-super/dist/unix"
```

### 6. "Error in row X: Invalid [field]" from csv2recipe.py

**Problem:** CSV contains invalid data that failed validation.

**Common issues:**

**Invalid characters in args:**
```csv
# WRONG - contains shell metacharacters
args: $(whoami)
args: BUILD=1 && rm -rf /

# RIGHT - only safe characters
args: BUILD=1 DYNAREC=ari64 HAVE_NEON=1
```

**Invalid URL:**
```csv
# WRONG - not HTTPS
url: http://github.com/libretro/core.git
url: git@github.com:libretro/core.git

# RIGHT - HTTPS only
url: https://github.com/libretro/core.git
```

**Path traversal attempt:**
```csv
# WRONG - path traversal
dir: ../../evil
subdir: ../../../etc

# RIGHT - relative paths only, no ..
dir: libretro-core
subdir: src/libretro
```

**Solution:** Fix the CSV file to use only valid characters and formats.

### 7. Build fails with "arm-linux-gnueabihf-gcc: command not found"

**Problem:** Cross-compilation toolchain not found in Docker container.

**Possible causes:**
- Docker image is incorrect
- Docker image failed to download
- Network issues

**Solutions:**

```bash
# Pull Docker image manually
docker pull techdevangelist/miyoomini-buildroot:latest

# Verify image exists
docker images | grep miyoomini

# Try running image interactively to test
docker run -it techdevangelist/miyoomini-buildroot:latest /bin/bash
# Inside container:
arm-linux-gnueabihf-gcc --version
# Should show GCC version
```

### 8. "Build completed successfully" but no files in build/<target>

**Problem:** Files were built but not copied.

**Debugging:**

```bash
# Check if dist/unix has files
ls libretro-super/dist/unix/

# If files exist there but not in build/<target>:
# Manually copy them
mkdir -p build/<target>
cp libretro-super/dist/unix/* build/<target>/

# Check for permission issues
ls -la libretro-super/dist/unix/
# All files should be readable
```

### 9. CSV file changes not reflected in build

**Problem:** Modified CSV but build uses old recipe.

**Cause:** Generated recipe file cached.

**Solution:**

```bash
# Delete cached recipe
rm config/<target>/libretro-cores

# Or clean everything
make clean

# Rebuild
make build/<target>
```

### 10. "disk space" or "no space left" errors

**Problem:** Out of disk space.

**Solutions:**

```bash
# Check disk usage
df -h

# Clean Docker images/containers
docker system prune -a

# Clean build artifacts
make clean

# Remove old Docker images
docker images
docker rmi <image_id>
```

### 11. Git submodule shows as modified after build

**Problem:** Build process modified files in libretro-super.

**Cause:** libretro-buildbot clones repos into libretro-super directory.

**Solution:**

```bash
# This is normal - libretro-super is in .gitignore for these changes

# To clean up:
make reset-submodules

# Or manually:
git submodule foreach --recursive git clean -xfd
git submodule foreach --recursive git reset --hard
```

### 12. Patch conflicts when updating libretro-super

**Problem:** Updated submodule and patch no longer applies.

**Solution:**

See ARCHITECTURE.md section "Updating libretro-super" for detailed process.

**Quick fix:**
1. Note your changes (look at buildbot-tweaks.patch)
2. Reset submodule: `make reset-submodules`
3. Update: `git submodule update --remote`
4. Try to apply patch: `cd libretro-super && patch -p0 < ../buildbot-tweaks.patch`
5. If patch fails:
   - Manually edit `libretro-buildbot-recipe.sh`
   - Apply the changes from the patch by hand
   - Regenerate patch: `git diff > ../buildbot-tweaks.patch`

### 13. CI build fails with "Error: No valid recipe found"

**Problem:** GitHub Actions can't find recipe file.

**Possible causes:**
- CSV file not committed
- Config directory missing
- File path case mismatch

**Solutions:**

```bash
# Verify files exist
ls -la config/<target>/

# Ensure CSV is committed
git status
git add config/<target>/libretro-cores.csv
git commit -m "Add recipe"
git push
```

### 14. Core builds but crashes when run on Miyoo Mini

**Problem:** Built core doesn't work on device.

**Not a build system issue - this is a core compatibility problem.**

**Debugging:**
1. Check core actually uses ARM/NEON instructions
2. Verify core supports the target platform
3. Check RetroArch version compatibility
4. Look for core-specific configuration issues
5. Check Miyoo Mini forums for known issues with specific cores

### 15. Very slow build times

**Problem:** Build takes hours.

**Possible causes:**
- Building too many cores at once
- Docker not using enough CPU/RAM
- ccache not working

**Solutions:**

```bash
# Build fewer cores - edit CSV to reduce core count

# Increase Docker resources
# Docker Desktop → Settings → Resources
# Increase CPUs and Memory

# Build specific target instead of all
make build/linux-armv7-neon_test  # smaller test set

# Use FORCE=NO to skip rebuilding (if supported)
FORCE=NO make build/<target>
```

## Getting More Help

### Enable verbose output:

```bash
# In build.sh, add to top:
set -x  # Print each command before execution
```

### Save build logs:

```bash
make build/<target> 2>&1 | tee build-log.txt
```

### Check Docker logs:

```bash
docker ps -a  # List all containers
docker logs <container_id>
```

### Check git status:

```bash
git status
git submodule status
```

### Verify Docker setup:

```bash
docker run hello-world
docker run -it ubuntu:20.04 /bin/bash
```

## Still Having Issues?

1. Check CODE_REVIEW.md for known issues
2. Review ARCHITECTURE.md to understand how system works
3. Open issue on GitHub with:
   - Full error message
   - Steps to reproduce
   - Output of `docker --version`
   - Output of `git submodule status`
   - Contents of relevant CSV file

## Emergency Reset

If everything is broken and you want to start fresh:

```bash
# Clean everything
make clean
make reset-submodules

# Remove Docker images
docker system prune -a

# Re-initialize
make init

# Try again
make build/<target>
```

This will reset the repository to a clean state.
