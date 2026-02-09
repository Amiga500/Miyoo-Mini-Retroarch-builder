# Contributing to Miyoo Mini RetroArch Builder

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and constructive
- Focus on improving the project
- Help others learn and grow

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check existing issues to avoid duplicates
2. Verify you're using the latest version
3. Test with a clean build (`make clean && make init`)

**Good bug report includes:**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Build logs (if applicable)
- Your environment:
  - OS and version
  - Docker version
  - Git submodule status

### Suggesting Features

Feature suggestions are welcome! Please:
1. Check if similar feature was already suggested
2. Explain the use case and why it's needed
3. Provide examples if possible
4. Consider implementation complexity

### Contributing Code

#### Before You Start

1. **Discuss major changes first** - Open an issue to discuss significant changes before implementing
2. **Check CODE_REVIEW.md** - Review known issues and recommendations
3. **Read ARCHITECTURE.md** - Understand how the system works

#### Development Setup

```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Miyoo-Mini-Retroarch-builder.git
cd Miyoo-Mini-Retroarch-builder

# Add upstream remote
git remote add upstream https://github.com/Amiga500/Miyoo-Mini-Retroarch-builder.git

# Create feature branch
git checkout -b feature/your-feature-name

# Initialize build environment
make init
```

#### Coding Standards

**Shell Scripts (bash):**
- Use `#!/bin/bash` shebang
- Add `set -euo pipefail` at the top
- Quote all variables: `"$variable"` not `$variable`
- Use `|| { echo "error"; exit 1; }` for error handling
- Pass shellcheck with no warnings: `shellcheck script.sh`
- Use descriptive variable names
- Add comments for complex logic
- Use 4-space indentation

**Python:**
- Use Python 3.6+ syntax
- Follow PEP 8 style guide
- Add docstrings for functions
- Use type hints where appropriate
- Handle errors with try/except and informative messages
- Add comments for complex logic
- Use 4-space indentation

**Makefile:**
- Use tabs (not spaces) for indentation
- Declare `.PHONY` targets
- Quote variables in shell commands
- Add comments explaining non-obvious targets

**General:**
- Keep changes focused and minimal
- One logical change per commit
- Write clear commit messages
- Test your changes

#### Testing Your Changes

**Test shell scripts:**
```bash
# Run shellcheck
shellcheck build.sh init.sh

# Test with various inputs
./build.sh ./config/linux-armv7-neon_test
```

**Test Python script:**
```bash
# Check syntax
python3 -m py_compile csv2recipe.py

# Test with valid CSV
python3 csv2recipe.py config/linux-armv7-neon/libretro-cores.csv /tmp/test.txt

# Test validation (should fail)
echo 'name,dir,url,git_branch,enabled,command,makefile,subdir,args
evil,../../etc,http://evil.com/x.git,main,YES,BAD,Makefile,.,$(rm -rf /)' > /tmp/evil.csv
python3 csv2recipe.py /tmp/evil.csv /tmp/output.txt
# Should print error and exit with non-zero code
```

**Test Makefile:**
```bash
# Test init
make init

# Test build with test recipe (small, fast)
make build/linux-armv7-neon_test

# Test clean
make clean
```

**Test in CI:**
- Push to your fork
- GitHub Actions will run
- Verify build completes successfully

#### Security Considerations

**CRITICAL: Always validate user input**

If your change accepts user input (CSV, command-line args, environment variables):
1. Validate format with regex
2. Whitelist safe characters
3. Prevent path traversal (no `..`)
4. Prevent command injection (no `$()`, backticks, `;`, `|`, etc.)
5. Add tests for malicious input

**Shell script security:**
```bash
# WRONG - command injection risk
eval $USER_INPUT
docker run image /bin/bash -c "echo $USER_INPUT"

# RIGHT - properly quoted
docker run image /bin/bash -c "echo \"$USER_INPUT\""
# BETTER - avoid shell entirely
docker run --env VAR="$USER_INPUT" image printenv VAR
```

**Python security:**
```python
# WRONG - command injection risk
os.system(f"git clone {url}")

# RIGHT - use list args, not shell
subprocess.run(["git", "clone", url], check=True)
```

#### Submitting Pull Request

1. **Update documentation** - If your change affects usage, update README.md, ARCHITECTURE.md, etc.
2. **Run tests** - Ensure shellcheck passes, Python syntax is valid
3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: Add feature X"
   # Use conventional commit format:
   # feat: New feature
   # fix: Bug fix
   # docs: Documentation
   # refactor: Code refactoring
   # test: Adding tests
   # chore: Maintenance
   ```
4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create Pull Request on GitHub**
6. **Describe your changes:**
   - What problem does it solve?
   - How does it work?
   - Any breaking changes?
   - How to test it?

#### PR Review Process

- Maintainers will review your PR
- Address feedback by pushing new commits
- Once approved, maintainers will merge

#### PR Checklist

- [ ] Code follows project style
- [ ] shellcheck passes (for shell scripts)
- [ ] Python syntax valid (for Python)
- [ ] No new security vulnerabilities introduced
- [ ] Documentation updated (if needed)
- [ ] Tested locally
- [ ] Commit messages are clear
- [ ] PR description explains changes

### Adding New Cores

**Easy contribution:** Add cores to existing recipes!

1. Find the repository for the libretro core
2. Edit `config/<target>/libretro-cores.csv`
3. Add row:
   ```csv
   core_name,libretro-core_name,https://github.com/libretro/core_name.git,master,YES,GENERIC,Makefile.libretro,.
   ```
4. Test: `make build/linux-armv7-neon` (replace with your target)
5. Submit PR with:
   - CSV changes
   - Brief description of core
   - Link to upstream repository

### Improving Documentation

Documentation improvements are always welcome!

**Areas that need help:**
- More examples in README.md
- More troubleshooting scenarios
- Screenshots/diagrams
- Video tutorials
- Wiki articles

**Process:**
1. Edit markdown file
2. Preview locally (use VS Code or `grip`)
3. Submit PR

### Fixing Bugs

**Priority bugs** (see CODE_REVIEW.md):
- Security vulnerabilities
- Build failures
- Data loss risks

**Process:**
1. Create issue (if doesn't exist)
2. Reference issue in commit: "fix: #123 - description"
3. Add test to prevent regression (if possible)
4. Submit PR

### Improving Security

Security improvements are highly valued!

**How to help:**
1. Review CODE_REVIEW.md section 4
2. Identify security issues
3. Submit PR with fixes
4. Add validation/sanitization tests

## Code Review Guidelines

When reviewing others' PRs:
- Be constructive and kind
- Focus on code, not person
- Explain the "why" behind suggestions
- Approve if changes are net positive (don't let perfect be enemy of good)

## Project Priorities

**Current focus:**
1. Security fixes (see CODE_REVIEW.md section 4)
2. Error handling improvements
3. Better documentation
4. Replacing patch-based workflow with fork

**Future goals:**
- Automated testing
- Binary distribution system
- Web dashboard
- Better CI integration

## Questions?

- Open an issue with `[Question]` prefix
- Review existing documentation
- Check CODE_REVIEW.md for known issues

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Thank You!

Your contributions help make this project better for the entire Miyoo Mini community!
