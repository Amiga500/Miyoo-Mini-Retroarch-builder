# RetroArch cores build-bot for Linux ARMv7

Automated Docker-based build system for compiling libretro/RetroArch cores optimized for **Miyoo Mini** and other ARMv7 NEON devices.

## ⚠️ Security Notice

**Version 2.0+ includes critical security fixes.** If upgrading from an older version:
- Command injection vulnerabilities patched
- Input validation added to CSV processing
- Error handling significantly improved

See [CODE_REVIEW.md](CODE_REVIEW.md) for complete security analysis.

## Features

- 🐋 **Docker-based builds** - Reproducible build environment
- 📋 **CSV recipe format** - Easy-to-edit core definitions
- 🎯 **Multi-target support** - Build for different ARM platforms
- 🔒 **Security hardened** - Input validation and sanitization
- 🤖 **GitHub Actions** - Automated CI/CD builds
- 🛡️ **Error handling** - Robust error checking and reporting

## Quick Start

### Prerequisites

- Docker installed and running
- Git with submodule support
- 10+ GB free disk space

### Build cores

```bash
# First time setup
make init

# Build cores for linux-armv7-neon target
make build/linux-armv7-neon

# Package cores into 7z archive
make dist

# Built cores will be in: dist/libretro_cores_linux-armv7-neon.7z
```

### Clean up

```bash
# Clean build artifacts
make clean

# Reset submodules to clean state
make reset-submodules
```

## Available Targets

- `linux-armv7-neon` - Full core set for Miyoo Mini
- `linux-armv7-neon_test` - Small test set (faster builds)
- `classic_armv7_a7` - Alternative ARM Cortex-A7 configuration

## Usage

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make init` | Initialize submodules and apply patches (run once) |
| `make build/<target>` | Build cores for specific target |
| `make dist` | Create 7z archives of built cores |
| `make clean` | Remove build and dist directories |
| `make reset-submodules` | Reset git submodules to clean state |

## Recipes

A recipe defines all the information needed to fetch, configure, and build a specific core for RetroArch. Each recipe entry specifies:

- The core's name and source repository
- The branch or commit to use
- Whether the core is enabled for building
- The build system and makefile to use
- Any subdirectory or extra build arguments

The buildbot script uses these recipes to automate and repeat the build process for different targets.


### Example recipe entry

| name | dir           | url                                           | git_branch | enabled | command | makefile          | subdir | args |
| ---- | ------------- | --------------------------------------------- | ---------- | ------- | ------- | ----------------- | ------ | ---- |
| 2048 | libretro-2048 | https://github.com/libretro/libretro-2048.git | master     | YES     | GENERIC | Makefile.libretro | .      |      |

**Note:** All CSV fields are validated for security. Only HTTPS Git URLs are allowed, and special characters are restricted in the `args` field.

## Adding New Cores

Edit `config/<target>/libretro-cores.csv` and add a new row:

```csv
core_name,libretro-core_name,https://github.com/libretro/core_name.git,master,YES,GENERIC,Makefile.libretro,.
```

Then rebuild:

```bash
make build/<target>
```

## GitHub Actions

This repository includes GitHub Actions workflow for automated builds:

1. Go to **Actions** tab
2. Select **"Build Cores via Docker"**
3. Click **"Run workflow"**
4. Choose target (or "all")
5. Download artifacts when complete

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and how it works
- **[CODE_REVIEW.md](CODE_REVIEW.md)** - Comprehensive security and code quality review
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

## Security

This project includes security hardening:
- ✅ Input validation for CSV recipes
- ✅ Shell command injection prevention
- ✅ Path traversal protection
- ✅ HTTPS-only Git URLs
- ✅ Comprehensive error handling

**Found a security issue?** Please open a private security advisory on GitHub.

## Architecture Overview

```
Makefile → Docker Container → build.sh → csv2recipe.py → libretro-buildbot
                                                               ↓
                                                     Built cores (.so files)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## Troubleshooting

**Common issues:**

- `patch: malformed patch` → Run `make reset-submodules` then `make init`
- `Docker: command not found` → Install Docker and add user to docker group
- `No .so files found` → Check build logs for compilation errors
- `Error in row X: Invalid [field]` → CSV contains invalid characters (see TROUBLESHOOTING.md)

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete guide.

## Credits

- Built on [libretro-super](https://github.com/libretro/libretro-super)
- Uses [techdevangelist/miyoomini-buildroot](https://hub.docker.com/r/techdevangelist/miyoomini-buildroot) Docker image
- Security review and improvements: GitHub Copilot

## License

This build system is provided as-is for building libretro cores. Individual cores have their own licenses - please review each core's repository for license information.
