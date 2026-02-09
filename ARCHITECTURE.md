# Architecture Documentation

## Overview

This is a Docker-based automated build system for compiling libretro/RetroArch cores optimized for the Miyoo Mini handheld gaming device (ARMv7 with NEON).

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Makefile                             │
│  (Orchestration layer - defines build pipeline)              │
└───────────┬─────────────────────────────────────┬───────────┘
            │                                     │
            v                                     v
    ┌───────────────┐                   ┌────────────────┐
    │   init.sh     │                   │   build.sh     │
    └───────────────┘                   └────────────────┘
            │                                     │
            v                                     v
    ┌────────────────────┐              ┌────────────────────┐
    │ Initialize         │              │ CSV → Recipe       │
    │ libretro-super     │              │ (csv2recipe.py)    │
    │ submodule          │              └─────────┬──────────┘
    │ Apply patch        │                        │
    └────────────────────┘                        v
                                         ┌────────────────────┐
                                         │ libretro-buildbot  │
                                         │ (from libretro-    │
                                         │  super)            │
                                         └─────────┬──────────┘
                                                   │
                                                   v
                                         ┌────────────────────┐
                                         │ Built cores (.so)  │
                                         │ + info files       │
                                         └────────────────────┘
```

## Components

### 1. Makefile

**Purpose:** Central orchestration and automation

**Key targets:**
- `init` - Initialize submodules and apply patches
- `build/<target>` - Build cores for specific target (e.g., linux-armv7-neon)
- `dist` - Package built cores into 7z archives
- `clean` - Remove build artifacts
- `reset-submodules` - Reset submodules to clean state

**How it works:**
1. Uses pattern rules to map `config/*` directories to `build/*` outputs
2. Invokes Docker container with Miyoo Mini buildroot toolchain
3. Passes build to `build.sh` inside container

### 2. init.sh

**Purpose:** One-time initialization of build environment

**What it does:**
1. Initializes git submodule (libretro-super)
2. Updates submodule to correct commit
3. Applies `buildbot-tweaks.patch` to customize libretro build script
4. Checks if patch already applied (idempotent)

**Run when:**
- First time setting up repository
- After `git clean -xfd`
- After updating libretro-super submodule

### 3. build.sh

**Purpose:** Build cores for a specific target configuration

**Parameters:**
- `$1` - Path to config directory (e.g., `./config/linux-armv7-neon`)

**What it does:**
1. Converts CSV recipe to legacy format (if CSV exists)
2. Invokes libretro-buildbot-recipe.sh with recipe
3. Copies built .so files and .info files to build directory
4. Validates build produced outputs

**Error handling:**
- Exits on any error (`set -euo pipefail`)
- Checks directories exist before cd
- Verifies .so files were built
- Provides helpful error messages

### 4. csv2recipe.py

**Purpose:** Convert user-friendly CSV recipes to legacy recipe format

**Input:** CSV file with columns:
- `name` - Core name
- `dir` - Directory name for git clone
- `url` - Git repository URL
- `git_branch` - Branch/tag to checkout
- `enabled` - YES/NO to enable/disable
- `command` - Build command type (GENERIC, CMAKE, etc.)
- `makefile` - Makefile name to use
- `subdir` - Subdirectory containing Makefile
- `args` - Additional make arguments

**Output:** Space-separated legacy recipe format

**Security:**
- Validates all inputs to prevent command injection
- Prevents path traversal attacks
- Enforces HTTPS-only Git URLs
- Whitelists safe characters in args field

### 5. buildbot-tweaks.patch

**Purpose:** Customize libretro-super buildbot script for Miyoo Mini

**Changes:**
1. Adds GitHub Actions collapsible groups (`::group::`)
2. Forces specific branch (`miyoomini-1.16.0`) for RetroArch
3. Disables audio/video filter compilation (not needed)
4. Disables RetroArch configure step
5. Changes build to use Miyoo-specific Makefiles
6. Builds 3 variants: miyoomini, miyoomini_ml, miyoomini_plus

**Fragility warning:** This patch applies to specific line numbers in libretro-buildbot-recipe.sh. Any upstream changes may break the patch.

### 6. config/ directory

**Structure:**
```
config/
├── linux-armv7-neon/
│   ├── libretro-cores.csv    # Recipe: which cores to build
│   └── libretro-cores.conf   # Toolchain config
├── linux-armv7-neon_test/
│   └── ...
└── classic_armv7_a7/
    └── ...
```

**libretro-cores.csv:** Defines which cores to build

**libretro-cores.conf:** Defines toolchain settings:
- Platform identifier
- Compiler paths (arm-linux-gnueabihf-gcc)
- Architecture flags (ARM_NEON, CORTEX_A7, ARM_HARDFLOAT)
- Build tools (make, cmake, strip)

## Build Flow

### Full build flow for one target:

```
1. make build/linux-armv7-neon
   ↓
2. Docker container starts with buildroot image
   ↓
3. build.sh ./config/linux-armv7-neon
   ↓
4. csv2recipe.py converts CSV to recipe
   ↓
5. libretro-buildbot-recipe.sh processes recipe
   ↓
6. For each core in recipe:
   - Clone git repo
   - Checkout branch
   - Read target .conf file
   - Run make with toolchain
   - Copy .so to dist/unix/
   ↓
7. build.sh copies .so files to build/linux-armv7-neon/
   ↓
8. make dist creates build/libretro_cores_linux-armv7-neon.7z
```

## Docker Image

**Image:** `techdevangelist/miyoomini-buildroot:latest`

**Contains:**
- ARM cross-compilation toolchain (arm-linux-gnueabihf)
- Build tools (make, cmake, git, etc.)
- Optimized for Miyoo Mini target

**Volume mounts:**
- Project directory → `/root/workspace` (read-write)

## Cross-Compilation Details

**Target architecture:** ARMv7-A (Cortex-A7)

**ABI:** ARM hard-float (gnueabihf)

**SIMD:** NEON enabled

**Compiler flags** (set in cores' Makefiles):
- `-march=armv7-a` - ARMv7 architecture
- `-mfpu=neon` - NEON SIMD instructions
- `-mfloat-abi=hard` - Hardware floating point

**Cores with special optimizations:**
- pcsx_rearmed: `DYNAREC=ari64 HAVE_NEON=1 BUILTIN_GPU=neon`
- gpsp: Uses ARM dynarec by default

## Adding a New Core

1. Edit `config/<target>/libretro-cores.csv`
2. Add new row with core details:
   ```csv
   snes9x,libretro-snes9x,https://github.com/libretro/snes9x.git,master,YES,GENERIC,Makefile.libretro,.
   ```
3. Run: `make build/<target>`

## Adding a New Target Platform

1. Create directory: `mkdir config/my-platform`
2. Create `libretro-cores.csv` with cores to build
3. Create `libretro-cores.conf` with toolchain settings
4. Run: `make build/my-platform`

## Updating libretro-super

**⚠️ Warning:** This is the most fragile operation

**Process:**
1. Back up current patch: `cp buildbot-tweaks.patch buildbot-tweaks.patch.bak`
2. Revert patch: `cd libretro-super && patch -p1 -R < ../buildbot-tweaks.patch`
3. Update submodule: `git submodule update --remote libretro-super`
4. Re-apply patch: `patch -p1 < ../buildbot-tweaks.patch`
5. If patch fails:
   - Manually apply changes from patch
   - Regenerate patch: `git diff > ../buildbot-tweaks.patch`
   - Test thoroughly

**Better approach:** Consider forking libretro-super (see CODE_REVIEW.md section 5)

## CI/CD

**GitHub Actions workflow:** `.github/workflows/build.yml`

**Triggers:** Manual dispatch (workflow_dispatch)

**Matrix build:** Supports building all targets or specific target

**Artifacts:** Uploads built cores for 90 days

**Usage:**
1. Go to Actions tab in GitHub
2. Select "Build Cores via Docker"
3. Click "Run workflow"
4. Choose which recipe(s) to build
5. Download artifacts when complete

## Troubleshooting

See `TROUBLESHOOTING.md` for common issues and solutions.

## Security Considerations

1. **CSV recipes are validated** - Malicious CSV entries are rejected
2. **Docker isolation** - Builds run in container, not host
3. **HTTPS-only Git** - Only https:// URLs allowed
4. **Input sanitization** - Shell metacharacters blocked in args

## Known Limitations

1. Patch-based customization is fragile (see CODE_REVIEW.md)
2. No automated testing of built cores
3. No verification of core functionality
4. Docker image is third-party (supply chain risk)
5. No automatic upstream updates

## Future Improvements

See CODE_REVIEW.md section 9 for detailed recommendations.
