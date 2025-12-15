# Preflight

**Multi-agent CI/CD pipeline ensuring Python packages pass cross-platform, multi-version, and quality gates before shipping.**

No code ships until it proves cross-platform compatibility, Python version matrix compliance, and package build integrity.

## Features

- **8 Quality Gates** - Sequential enforcement, no skipping
- **Cross-Platform Validation** - Windows + Ubuntu compatibility checks
- **Python Matrix Testing** - Python 3.9-3.13 verification
- **Security Scanning** - Secrets, vulnerabilities, and license checks
- **API Compatibility** - Breaking change detection
- **Package Verification** - Build, install, and entry point testing
- **GitHub Integration** - PR creation with full gate report

## Installation

### From Marketplace

```bash
# Add marketplace to Claude Code
/plugin marketplace add dansasser/claude-code-marketplace

# Install Preflight
/plugin install preflight
```

### Manual Installation

```bash
git clone https://github.com/dansasser/claude-code-marketplace.git
cd claude-code-marketplace/plugins/preflight

# Copy to your project
cp -r .claude/ /path/to/your/project/
cp CLAUDE.md /path/to/your/project/
```

## Quick Start

```bash
# Run full pipeline
/preflight

# Run specific gate
/gate 3

# Check status
/status

# Ship when ready
/ship
```

## The 8 Quality Gates

| Gate | Name | Purpose | Pass Condition |
|------|------|---------|----------------|
| 1 | lint-test | Code quality | Zero lint/type errors, tests pass |
| 2 | coverage | Test coverage | >= 80% coverage |
| 3 | cross-platform | OS compatibility | Windows + Ubuntu identical |
| 4 | python-matrix | Version support | 3.9-3.13 all pass |
| 5 | security | Safety | No secrets/critical vulns |
| 6 | api-compat | Stability | No unintended breaking changes |
| 7 | packaging | Distribution | Builds, installs, entry points work |
| 8 | github-pr | Ship | Creates PR with full report |

## Commands

| Command | Description |
|---------|-------------|
| `/preflight` | Run full 8-gate pipeline |
| `/gate <n>` | Run specific gate by number or name |
| `/status` | Show pipeline status |
| `/ship` | Run pipeline and create PR |
| `/lint` | Quick lint check |
| `/xplat` | Quick cross-platform check |
| `/security` | Quick security scan |
| `/coverage` | Quick coverage check |

## Gate Prerequisites

Each gate requires previous gates to pass:

```
Gate 1: lint-test     (no prerequisites)
Gate 2: coverage      (requires gate 1)
Gate 3: cross-platform(requires gates 1-2)
Gate 4: python-matrix (requires gates 1-3)
Gate 5: security      (requires gates 1-4)
Gate 6: api-compat    (requires gates 1-5)
Gate 7: packaging     (requires gates 1-6)
Gate 8: github-pr     (requires ALL gates 1-7)
```

## What Preflight Catches

### Cross-Platform Issues (Gate 3)

| Issue | Example | Fix |
|-------|---------|-----|
| Path separators | `"data/file.txt"` | `Path("data") / "file.txt"` |
| Home directory | `os.environ["HOME"]` | `Path.home()` |
| Temp paths | `"/tmp/cache"` | `Path(tempfile.gettempdir())` |
| Shell commands | `os.system("rm -rf")` | `shutil.rmtree()` |
| Line endings | Mixed CRLF/LF | `.gitattributes` |

### Python Compatibility (Gate 4)

| Issue | Affected | Fix |
|-------|----------|-----|
| `match` statement | < 3.10 | Use if/elif |
| `\|` union types | < 3.10 | Use `Union[X, Y]` |
| `tomllib` | < 3.11 | Use `tomli` package |

### Security Issues (Gate 5)

- Exposed API keys and tokens
- Hardcoded passwords
- Known CVEs in dependencies
- GPL licenses in MIT projects

### Package Issues (Gate 7)

- Invalid pyproject.toml
- Missing files in distribution
- Broken entry points
- Import failures after install

## Configuration

Configuration files in `config/`:

| File | Purpose |
|------|---------|
| `gates.yaml` | Gate sequence and timeouts |
| `coverage.yaml` | Coverage thresholds |
| `xplat.yaml` | Cross-platform patterns |
| `python-versions.yaml` | Python versions to test |
| `security.yaml` | Security scan rules |
| `api-compat.yaml` | Breaking change definitions |
| `packaging.yaml` | Package requirements |
| `lint.yaml` | Ruff/mypy settings |

## PR Output

When all gates pass, `/ship` creates a PR with:

```markdown
## Summary
[Auto-generated from commits]

## Preflight Results

| Gate | Status | Details |
|------|--------|---------|
| 1. Lint/Test | PASS | 0 errors, 142 tests passed |
| 2. Coverage | PASS | 87.3% (threshold: 80%) |
| 3. Cross-Platform | PASS | Windows + Ubuntu verified |
| 4. Python Matrix | PASS | 3.9, 3.10, 3.11, 3.12, 3.13 |
| 5. Security | PASS | 0 secrets, 0 critical vulns |
| 6. API Compat | PASS | No breaking changes |
| 7. Package Build | PASS | Wheel + sdist verified |
```

## Dependencies

Required:
- Python >= 3.9
- ruff >= 0.1.0
- mypy >= 1.0.0
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- build >= 1.0.0
- twine >= 4.0.0
- pip-audit >= 2.0.0

## License

MIT License - see [LICENSE](LICENSE)

## Author

Daniel T Sasser II - [dansasser.me](https://dansasser.me)

Part of the [claude-code-marketplace](https://github.com/dansasser/claude-code-marketplace).
