# Claude Code Agents: Cross-Platform Python Package CI/CD Pipeline

## Project Overview

A governance-first multi-agent system for Claude Code that ensures Python packages pass all quality gates before reaching GitHub or PyPI. No code ships until it proves cross-platform compatibility, Python version matrix compliance, and package build integrity.

## Problem Statement

Python packages fail in production due to:
- Path separator differences (/ vs \)
- Line ending issues (LF vs CRLF)
- Case sensitivity (Linux yes, Windows no)
- Shell command incompatibility
- Environment variable differences (HOME vs USERPROFILE)
- Python version incompatibilities (3.9 vs 3.13)
- Package build failures (wheel builds locally, fails on install)
- Broken entry points (CLI commands don't work after install)
- Missing files in distribution (MANIFEST.in misconfigured)
- Dependency conflicts and deprecated packages
- Unintended breaking API changes
- Inadequate test coverage

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PIPELINE ORCHESTRATOR                          │
│               (Enforces gate sequence, no skipping)                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
    ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼          ▼          ▼          ▼          ▼          
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│ Gate 1 ││ Gate 2 ││ Gate 3 ││ Gate 4 ││ Gate 5 ││ Gate 6 ││ Gate 7 ││ Gate 8 │
│  Lint  ││Coverage││ XPlat  ││ PyVer  ││Security││  API   ││Package ││Git/PR/ │
│  Test  ││        ││  Test  ││ Matrix ││ Audit  ││ Compat ││ Build  ││Publish │
└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘
    │          │          │          │          │          │          │          │
  FAIL       FAIL       FAIL       FAIL       FAIL       FAIL       FAIL       │
    │          │          │          │          │          │          │          │
    └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘          │
                                  │                                              │
                                  ▼                                              │
    ┌─────────────────────────────────────────────────────────────────┐          │
    │           STOP - Return context to developer                    │          │
    └─────────────────────────────────────────────────────────────────┘          │
                                                                                 │
                                                                    PASS (all gates)
                                                                                 │
                                                                                 ▼
                                                                         ┌──────────────┐
                                                                         │   SUCCESS    │
                                                                         │ Push/Publish │
                                                                         └──────────────┘
```

---

## Gate Definitions

| Gate | Name | Purpose | Pass Condition |
|------|------|---------|----------------|
| 1 | Lint/Test | Code quality and tests | Zero lint errors, zero type errors, all tests pass |
| 2 | Coverage | Test coverage enforcement | Meets minimum threshold (default 80%) |
| 3 | Cross-Platform | Windows + Ubuntu compat | Identical test results on both OS |
| 4 | Python Matrix | Multi-version support | Tests pass on all declared Python versions |
| 5 | Security | Vulnerabilities and secrets | No secrets, no critical vulnerabilities |
| 6 | API Compatibility | Breaking change detection | No unintended public API changes |
| 7 | Package Build | Distribution integrity | Builds, installs, imports, entry points work |
| 8 | Git/PR/Publish | Ship it | All prior gates PASS, commits, PRs, publishes |

---

## Directory Structure

```
claude-code-agents/
├── CLAUDE.md                          # Master instructions for Claude Code
├── plugin.json                        # Marketplace plugin manifest
├── README.md                          # Plugin documentation
├── LICENSE                            # License file
├── pyproject.toml                     # Plugin's own package config
├── requirements.txt                   # Plugin dependencies
├── requirements-dev.txt               # Development dependencies
│
├── .claude/
│   ├── settings.json                  # Claude Code configuration
│   └── commands/                      # Slash commands
│       ├── lint.md
│       ├── coverage.md
│       ├── xplat.md
│       ├── pymatrix.md
│       ├── security.md
│       ├── api-check.md
│       ├── package.md
│       ├── ship.md
│       ├── plan.md
│       ├── deps.md
│       └── full-pipeline.md
│
├── scripts/
│   ├── __init__.py
│   ├── pipeline.py                    # Main orchestrator
│   ├── run_gate.py                    # Generic gate runner
│   ├── state_manager.py               # Read/write pipeline_state.json
│   ├── setup.sh                       # Linux/Mac initial setup
│   ├── setup.ps1                      # Windows initial setup
│   ├── install_deps.py                # Cross-platform dependency installer
│   ├── bump_version.py                # Semantic version bump utility
│   ├── generate_lockfile.py           # Create/update requirements lock
│   └── prep_release.py                # Full release checklist runner
│
├── agents/
│   ├── __init__.py
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── pipeline.py                # Gate sequencing logic
│   │   ├── state.py                   # Pipeline state management
│   │   └── handoff.py                 # Inter-agent communication
│   │
│   ├── lint_test/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── run_lint.py                # Runs ruff
│   │   ├── run_format.py              # Runs formatters (black, isort, ruff format)
│   │   ├── run_typecheck.py           # Runs mypy
│   │   └── run_tests.py               # Runs pytest
│   │
│   ├── coverage/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── run_coverage.py            # pytest --cov with threshold
│   │   ├── check_threshold.py         # Enforce minimum coverage
│   │   └── generate_report.py         # Coverage report generator
│   │
│   ├── cross_platform/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── check_paths.py             # Detects hardcoded path separators
│   │   ├── check_line_endings.py      # LF vs CRLF detection
│   │   ├── check_env_vars.py          # Finds $HOME, %USERPROFILE% etc
│   │   ├── check_case_sensitivity.py  # Duplicate filenames differing by case
│   │   ├── check_shell_commands.py    # Bash-specific syntax detection
│   │   ├── check_temp_paths.py        # Hardcoded /tmp or C:\Temp
│   │   ├── run_windows_tests.py       # Docker/container test runner
│   │   ├── run_ubuntu_tests.py        # Docker/container test runner
│   │   └── compare_results.py         # Diffs test outputs between OS
│   │
│   ├── python_matrix/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── run_python39_tests.py      # Test against Python 3.9
│   │   ├── run_python310_tests.py     # Test against Python 3.10
│   │   ├── run_python311_tests.py     # Test against Python 3.11
│   │   ├── run_python312_tests.py     # Test against Python 3.12
│   │   ├── run_python313_tests.py     # Test against Python 3.13
│   │   ├── matrix_runner.py           # Runs all versions in parallel
│   │   └── compare_results.py         # Ensures all versions pass
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── scan_secrets.py            # Wraps gitleaks/trufflehog
│   │   ├── audit_deps.py              # Wraps pip-audit/safety
│   │   └── check_licenses.py          # License compatibility check
│   │
│   ├── api_compat/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── extract_public_api.py      # What's exported from package?
│   │   ├── compare_api.py             # Breaking changes from last release?
│   │   ├── check_deprecations.py      # DeprecationWarning detection
│   │   └── generate_api_diff.py       # Human-readable API changes
│   │
│   ├── packaging/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── validate_pyproject.py      # pyproject.toml schema validation
│   │   ├── check_manifest.py          # MANIFEST.in / included files check
│   │   ├── build_package.py           # Build wheel and sdist
│   │   ├── test_install.py            # Install in clean venv, verify imports
│   │   ├── test_entry_points.py       # CLI commands actually run?
│   │   ├── validate_readme.py         # Will it render on PyPI? (twine check)
│   │   ├── check_version.py           # Version bumped? Consistent?
│   │   └── publish.py                 # Upload to TestPyPI, then PyPI
│   │
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── check_lock_sync.py         # requirements.txt matches pyproject.toml?
│   │   ├── check_bounds.py            # Version bounds too loose/tight?
│   │   ├── check_deprecated.py        # Using deprecated packages?
│   │   ├── check_conflicts.py         # Dependency conflicts detection
│   │   └── generate_lock.py           # Regenerate lock file
│   │
│   ├── git_workflow/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── analyze_diff.py            # Parses git diff
│   │   ├── generate_commit.py         # Semantic commit message
│   │   ├── generate_pr.py             # PR description builder
│   │   ├── verify_gates.py            # Checks all gates passed
│   │   └── publish_release.py         # Tag, release, PyPI upload
│   │
│   ├── planning/
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent entry point
│   │   ├── analyze_architecture.py    # Codebase structure analysis
│   │   ├── map_dependencies.py        # Internal dependency graph
│   │   ├── score_complexity.py        # Cyclomatic complexity scoring
│   │   └── identify_tech_debt.py      # Technical debt detection
│   │
│   └── docs/
│       ├── __init__.py
│       ├── agent.py                   # Agent entry point
│       ├── generate_readme.py         # README generation
│       ├── generate_changelog.py      # CHANGELOG from commits
│       ├── generate_api_docs.py       # API documentation
│       └── sync_docs.py               # Keep docs in sync with code
│
├── config/
│   ├── pipeline.yaml                  # Gate sequence, timeouts, requirements
│   ├── lint_rules.yaml                # Ruff/linter settings
│   ├── xplat_rules.yaml               # Cross-platform patterns to catch
│   ├── security_rules.yaml            # What to scan for
│   ├── commit_conventions.yaml        # Semantic commit format rules
│   ├── python_versions.yaml           # Which Python versions to test
│   ├── coverage_rules.yaml            # Minimum coverage thresholds
│   ├── packaging_rules.yaml           # PyPI metadata requirements
│   ├── api_compat_rules.yaml          # What constitutes breaking change
│   └── dependency_rules.yaml          # Dependency management rules
│
├── state/
│   ├── .gitkeep
│   └── pipeline_state.json            # Current pipeline status (gitignored)
│
├── docker/
│   ├── Dockerfile.ubuntu              # Ubuntu test environment
│   ├── Dockerfile.windows             # Windows test environment
│   ├── Dockerfile.py39                # Python 3.9 environment
│   ├── Dockerfile.py310               # Python 3.10 environment
│   ├── Dockerfile.py311               # Python 3.11 environment
│   ├── Dockerfile.py312               # Python 3.12 environment
│   ├── Dockerfile.py313               # Python 3.13 environment
│   ├── docker-compose.yml             # Multi-container orchestration
│   └── docker-compose.matrix.yml      # Python version matrix
│
├── templates/
│   ├── pr_template.md                 # Pull request template
│   ├── commit_template.txt            # Commit message template
│   ├── failure_report.md              # Failure report format
│   ├── release_notes.md               # Release notes template
│   └── api_diff_report.md             # API changes report template
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_orchestrator.py
│   │   ├── test_state_manager.py
│   │   ├── test_lint_agent.py
│   │   ├── test_coverage_agent.py
│   │   ├── test_xplat_agent.py
│   │   ├── test_matrix_agent.py
│   │   ├── test_security_agent.py
│   │   ├── test_api_agent.py
│   │   ├── test_packaging_agent.py
│   │   └── test_git_agent.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_full_pipeline.py
│   │   ├── test_gate_handoffs.py
│   │   └── test_failure_handling.py
│   └── fixtures/
│       ├── sample_good_package/
│       ├── sample_bad_paths/
│       ├── sample_broken_entry_point/
│       └── sample_api_breaking_change/
│
└── docs/
    ├── AGENTS.md                      # Agent documentation
    ├── HANDOFFS.md                    # Handoff protocol documentation
    ├── CONFIGURATION.md               # Configuration reference
    ├── TROUBLESHOOTING.md             # Common failure patterns
    ├── EXTENDING.md                   # How to add new agents/gates
    └── MARKETPLACE.md                 # Plugin marketplace info
```

---

## Complete Script Inventory

### Core Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `pipeline.py` | Main orchestrator - runs gates in sequence, enforces no-skip rule |
| `run_gate.py` | Generic gate runner - executes any gate by name |
| `state_manager.py` | Read/write pipeline_state.json, state validation |
| `setup.sh` | Linux/Mac initial setup - installs deps, creates dirs |
| `setup.ps1` | Windows initial setup - PowerShell equivalent |
| `install_deps.py` | Cross-platform dependency installer |
| `bump_version.py` | Semantic version bump (major/minor/patch) |
| `generate_lockfile.py` | Create/update requirements.txt from pyproject.toml |
| `prep_release.py` | Full release checklist - runs before any release |

### Lint/Test Agent (`agents/lint_test/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates all lint/test operations |
| `run_lint.py` | Executes ruff check, collects errors |
| `run_format.py` | Executes ruff format, black, isort |
| `run_typecheck.py` | Executes mypy --strict |
| `run_tests.py` | Executes pytest, collects results |

### Coverage Agent (`agents/coverage/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates coverage operations |
| `run_coverage.py` | Executes pytest --cov |
| `check_threshold.py` | Compares coverage to minimum threshold |
| `generate_report.py` | Creates coverage report in multiple formats |

### Cross-Platform Agent (`agents/cross_platform/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates cross-platform checks |
| `check_paths.py` | Regex scan for hardcoded `/` or `\\` in paths |
| `check_line_endings.py` | Detects CRLF, verifies .gitattributes |
| `check_env_vars.py` | Finds `$HOME`, `%USERPROFILE%`, etc. |
| `check_case_sensitivity.py` | Finds files differing only by case |
| `check_shell_commands.py` | Detects bash-specific syntax |
| `check_temp_paths.py` | Finds hardcoded `/tmp` or `C:\Temp` |
| `run_windows_tests.py` | Spins up Windows container, runs pytest |
| `run_ubuntu_tests.py` | Spins up Ubuntu container, runs pytest |
| `compare_results.py` | Diffs test results between OS, reports differences |

### Python Matrix Agent (`agents/python_matrix/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates Python version testing |
| `run_python39_tests.py` | Tests against Python 3.9 container |
| `run_python310_tests.py` | Tests against Python 3.10 container |
| `run_python311_tests.py` | Tests against Python 3.11 container |
| `run_python312_tests.py` | Tests against Python 3.12 container |
| `run_python313_tests.py` | Tests against Python 3.13 container |
| `matrix_runner.py` | Parallel execution of all Python versions |
| `compare_results.py` | Ensures all versions produce same results |

### Security Agent (`agents/security/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates security scans |
| `scan_secrets.py` | Wraps gitleaks or trufflehog |
| `audit_deps.py` | Wraps pip-audit or safety |
| `check_licenses.py` | Validates dependency licenses are compatible |

### API Compatibility Agent (`agents/api_compat/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates API compatibility checks |
| `extract_public_api.py` | Parses `__all__`, public classes/functions |
| `compare_api.py` | Diffs current API against last release |
| `check_deprecations.py` | Runs tests with `-W error::DeprecationWarning` |
| `generate_api_diff.py` | Creates human-readable API change report |

### Packaging Agent (`agents/packaging/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates package build/test |
| `validate_pyproject.py` | Validates pyproject.toml against schema |
| `check_manifest.py` | Verifies all files included in distribution |
| `build_package.py` | Builds wheel and sdist |
| `test_install.py` | Creates clean venv, installs wheel, tests imports |
| `test_entry_points.py` | Runs every CLI entry point with `--help` |
| `validate_readme.py` | Runs `twine check` for PyPI rendering |
| `check_version.py` | Verifies version bumped and consistent |
| `publish.py` | Uploads to TestPyPI first, then PyPI |

### Dependencies Agent (`agents/dependencies/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates dependency checks |
| `check_lock_sync.py` | Verifies lock file matches pyproject.toml |
| `check_bounds.py` | Warns on too-loose or too-tight version bounds |
| `check_deprecated.py` | Flags deprecated or unmaintained packages |
| `check_conflicts.py` | Detects dependency conflicts |
| `generate_lock.py` | Regenerates requirements.txt/lock file |

### Git Workflow Agent (`agents/git_workflow/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates git operations |
| `analyze_diff.py` | Parses `git diff`, categorizes changes |
| `generate_commit.py` | Creates semantic commit message |
| `generate_pr.py` | Builds detailed PR description |
| `verify_gates.py` | Reads state file, refuses if any gate not PASS |
| `publish_release.py` | Tags release, creates GitHub release, triggers PyPI |

### Planning Agent (`agents/planning/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates analysis |
| `analyze_architecture.py` | Maps codebase structure |
| `map_dependencies.py` | Creates internal dependency graph |
| `score_complexity.py` | Calculates cyclomatic complexity |
| `identify_tech_debt.py` | Flags TODO, FIXME, complexity hotspots |

### Documentation Agent (`agents/docs/`)

| Script | Purpose |
|--------|---------|
| `agent.py` | Entry point - coordinates doc generation |
| `generate_readme.py` | Creates/updates README.md |
| `generate_changelog.py` | Builds CHANGELOG from commit history |
| `generate_api_docs.py` | Generates API documentation |
| `sync_docs.py` | Ensures docs match current code state |

---

## Configuration Files

### config/pipeline.yaml
```yaml
pipeline:
  name: python-package-ci
  version: 2.0.0
  
gates:
  - name: lint_test
    display_name: "Lint & Test"
    required: true
    timeout_seconds: 300
    on_fail: stop
    
  - name: coverage
    display_name: "Coverage Check"
    required: true
    timeout_seconds: 120
    on_fail: stop
    depends_on:
      - lint_test
    
  - name: cross_platform
    display_name: "Cross-Platform"
    required: true
    timeout_seconds: 600
    environments:
      - windows-latest
      - ubuntu-latest
    on_fail: stop
    depends_on:
      - coverage
    
  - name: python_matrix
    display_name: "Python Version Matrix"
    required: true
    timeout_seconds: 900
    python_versions:
      - "3.9"
      - "3.10"
      - "3.11"
      - "3.12"
      - "3.13"
    parallel: true
    on_fail: stop
    depends_on:
      - cross_platform
    
  - name: security
    display_name: "Security Audit"
    required: true
    timeout_seconds: 180
    on_fail: stop
    depends_on:
      - python_matrix
    
  - name: api_compat
    display_name: "API Compatibility"
    required: true
    timeout_seconds: 120
    on_fail: stop
    depends_on:
      - security
    
  - name: packaging
    display_name: "Package Build"
    required: true
    timeout_seconds: 300
    on_fail: stop
    depends_on:
      - api_compat
    
  - name: git_workflow
    display_name: "Git/PR/Publish"
    required: true
    requires_all_gates: true
    on_fail: stop

settings:
  parallel_environments: true
  parallel_python_versions: true
  verbose_logging: true
  state_file: state/pipeline_state.json
  fail_fast: true
```

### config/python_versions.yaml
```yaml
python_matrix:
  minimum_version: "3.9"
  maximum_version: "3.13"
  
  versions:
    - version: "3.9"
      docker_image: "python:3.9-slim"
      eol_date: "2025-10"
      required: true
      
    - version: "3.10"
      docker_image: "python:3.10-slim"
      eol_date: "2026-10"
      required: true
      
    - version: "3.11"
      docker_image: "python:3.11-slim"
      eol_date: "2027-10"
      required: true
      
    - version: "3.12"
      docker_image: "python:3.12-slim"
      eol_date: "2028-10"
      required: true
      
    - version: "3.13"
      docker_image: "python:3.13-slim"
      eol_date: "2029-10"
      required: true

  test_command: "pytest -v"
  install_command: "pip install -e .[dev]"
```

### config/coverage_rules.yaml
```yaml
coverage:
  minimum_threshold: 80
  fail_under: 80
  
  exclude_patterns:
    - "*/tests/*"
    - "*/__pycache__/*"
    - "*/migrations/*"
    - "*/.venv/*"
    
  branch_coverage: true
  
  per_file_minimum: 60
  
  report_formats:
    - terminal
    - html
    - xml
    - json
    
  badge_thresholds:
    excellent: 90
    good: 80
    acceptable: 70
    poor: 60
```

### config/xplat_rules.yaml
```yaml
cross_platform:
  path_handling:
    forbidden_patterns:
      - pattern: '(?<![\'\"a-zA-Z0-9])\/(?!\/|\*)'
        description: "Unquoted forward slashes in paths"
        severity: error
      - pattern: '\\\\\\\\'
        description: "Hardcoded backslashes"
        severity: error
      - pattern: 'os\.path\.join\([^)]*[\'"][^\'"]*/[^\'"]*[\'"]'
        description: "Forward slash inside os.path.join"
        severity: warning
        
    required_imports:
      - "from pathlib import Path"
      - "import os.path"
      
    recommended_patterns:
      - "Path(__file__).parent"
      - "Path.home()"
      - "os.path.join()"
    
  line_endings:
    enforce: LF
    gitattributes_required: true
    gitattributes_content: |
      * text=auto eol=lf
      *.py text eol=lf
      *.md text eol=lf
      *.yml text eol=lf
      *.yaml text eol=lf
      *.json text eol=lf
      *.sh text eol=lf
      *.ps1 text eol=crlf
      *.bat text eol=crlf
    
  case_sensitivity:
    check_duplicates: true
    check_imports: true
    check_config_references: true
    
  environment_variables:
    forbidden:
      - pattern: '\$HOME(?![A-Z_])'
        use_instead: "Path.home()"
      - pattern: '\$USER(?![A-Z_])'
        use_instead: "getpass.getuser()"
      - pattern: '%USERPROFILE%'
        use_instead: "Path.home()"
      - pattern: '%USERNAME%'
        use_instead: "getpass.getuser()"
      - pattern: '%TEMP%'
        use_instead: "tempfile.gettempdir()"
      - pattern: '%TMP%'
        use_instead: "tempfile.gettempdir()"
      
  temp_files:
    required_module: tempfile
    forbidden_paths:
      - "/tmp"
      - "/var/tmp"
      - "C:\\Temp"
      - "C:\\Windows\\Temp"
      
  shell_commands:
    forbidden_in_cross_platform:
      - "bash"
      - "sh -c"
      - "/bin/sh"
      - "/bin/bash"
    recommended: "subprocess.run with shell=False and list args"
    
  executables:
    check_extension_handling: true
    windows_extensions:
      - ".exe"
      - ".cmd"
      - ".bat"
      - ".ps1"
```

### config/packaging_rules.yaml
```yaml
packaging:
  pyproject_required_fields:
    - "project.name"
    - "project.version"
    - "project.description"
    - "project.readme"
    - "project.license"
    - "project.authors"
    - "project.requires-python"
    - "project.classifiers"
    - "project.dependencies"
    
  pyproject_recommended_fields:
    - "project.urls"
    - "project.keywords"
    - "project.optional-dependencies"
    
  classifiers:
    required_categories:
      - "Development Status"
      - "Intended Audience"
      - "License"
      - "Programming Language :: Python"
      - "Operating System"
      
  readme:
    formats:
      - "README.md"
      - "README.rst"
    min_length: 500
    required_sections:
      - "Installation"
      - "Usage"
      
  version:
    format: "semver"
    locations:
      - "pyproject.toml"
      - "__init__.py"
    must_match: true
    
  entry_points:
    test_with_help: true
    timeout_seconds: 10
    
  distribution:
    build_wheel: true
    build_sdist: true
    twine_check: true
    test_pypi_first: true
```

### config/api_compat_rules.yaml
```yaml
api_compatibility:
  public_api_detection:
    use_all_exports: true
    include_public_methods: true
    include_public_classes: true
    include_public_functions: true
    exclude_prefixes:
      - "_"
      - "__"
      
  breaking_changes:
    severity: error
    types:
      - "removed_function"
      - "removed_class"
      - "removed_method"
      - "removed_parameter"
      - "changed_parameter_type"
      - "changed_return_type"
      - "changed_parameter_default"
      - "made_parameter_required"
      
  non_breaking_changes:
    severity: info
    types:
      - "added_function"
      - "added_class"
      - "added_method"
      - "added_optional_parameter"
      
  deprecation:
    require_warning: true
    minimum_versions_before_removal: 2
    
  comparison_baseline:
    source: "latest_release_tag"
    fallback: "main_branch"
```

### config/security_rules.yaml
```yaml
security:
  secrets_scan:
    tool: "gitleaks"
    config_file: ".gitleaks.toml"
    scan_staged: true
    scan_commits: true
    patterns:
      - "api_key"
      - "api_secret"
      - "password"
      - "secret"
      - "token"
      - "private_key"
      - "aws_access_key"
      - "aws_secret_key"
      
  dependency_audit:
    tool: "pip-audit"
    ignore_vulnerabilities: []
    severity_threshold: "moderate"
    fail_on:
      - "critical"
      - "high"
    warn_on:
      - "moderate"
      
  license_check:
    allowed_licenses:
      - "MIT"
      - "Apache-2.0"
      - "BSD-2-Clause"
      - "BSD-3-Clause"
      - "ISC"
      - "PSF-2.0"
      - "Python-2.0"
    forbidden_licenses:
      - "GPL-2.0"
      - "GPL-3.0"
      - "AGPL-3.0"
    unknown_license_action: "warn"
```

### config/dependency_rules.yaml
```yaml
dependencies:
  lock_file:
    format: "requirements.txt"
    include_hashes: true
    
  version_bounds:
    warn_unbounded: true
    warn_too_tight: true
    recommended_format: ">=X.Y,<X+1"
    
  deprecated_packages:
    check_pypi_status: true
    warn_unmaintained_days: 365
    
  conflict_detection:
    check_before_install: true
    
  update_policy:
    security_updates: "immediate"
    minor_updates: "weekly"
    major_updates: "manual"
```

### config/commit_conventions.yaml
```yaml
commit:
  format: "conventional"
  
  types:
    - type: "feat"
      description: "New feature"
      bump: "minor"
    - type: "fix"
      description: "Bug fix"
      bump: "patch"
    - type: "docs"
      description: "Documentation only"
      bump: null
    - type: "style"
      description: "Formatting, no code change"
      bump: null
    - type: "refactor"
      description: "Code restructuring"
      bump: null
    - type: "perf"
      description: "Performance improvement"
      bump: "patch"
    - type: "test"
      description: "Adding tests"
      bump: null
    - type: "build"
      description: "Build system changes"
      bump: null
    - type: "ci"
      description: "CI configuration"
      bump: null
    - type: "chore"
      description: "Maintenance"
      bump: null
    - type: "revert"
      description: "Revert previous commit"
      bump: "patch"
      
  breaking_change:
    indicator: "!"
    footer: "BREAKING CHANGE:"
    bump: "major"
    
  scope:
    required: false
    allowed: []  # Empty means any scope allowed
    
  subject:
    max_length: 72
    capitalize: false
    end_period: false
```

### config/lint_rules.yaml
```yaml
lint:
  ruff:
    select:
      - "E"      # pycodestyle errors
      - "W"      # pycodestyle warnings
      - "F"      # Pyflakes
      - "I"      # isort
      - "B"      # flake8-bugbear
      - "C4"     # flake8-comprehensions
      - "UP"     # pyupgrade
      - "SIM"    # flake8-simplify
      - "TCH"    # flake8-type-checking
      - "PTH"    # flake8-use-pathlib
      - "RUF"    # Ruff-specific rules
    ignore:
      - "E501"   # Line too long (handled by formatter)
    line-length: 88
    target-version: "py39"
    fix: true
    
  mypy:
    strict: true
    ignore_missing_imports: false
    warn_return_any: true
    warn_unused_configs: true
    disallow_untyped_defs: true
    
  formatter:
    tool: "ruff format"
    line_length: 88
    quote_style: "double"
    
  isort:
    profile: "black"
    line_length: 88
```

---

## CLAUDE.md Content

```markdown
# CLAUDE.md - Python Package Pipeline Governance

## Identity

You are operating a multi-agent CI/CD pipeline for Python packages. Your primary directive is ensuring packages pass all 8 quality gates before reaching GitHub or PyPI.

## Cardinal Rules

1. **NEVER skip gates** - Each gate must explicitly PASS before the next runs
2. **NEVER push without cross-platform validation** - Gate 3 must confirm both OS pass
3. **NEVER push without Python version matrix** - Gate 4 must confirm all versions pass
4. **NEVER publish without package build verification** - Gate 7 must confirm wheel installs and entry points work
5. **NEVER ignore failures** - All failures stop the pipeline and report upstream
6. **NEVER proceed on warnings for required gates** - Warnings in required gates are failures until resolved

## Gate Sequence

```
Gate 1: Lint/Test       → Gate 2: Coverage      → Gate 3: Cross-Platform
Gate 4: Python Matrix   → Gate 5: Security      → Gate 6: API Compat
Gate 7: Package Build   → Gate 8: Git/PR/Publish
```

## Agent Activation Commands

### /lint - Lint/Test Agent (Gate 1)
Runs: ruff check, ruff format, mypy, pytest
Pass condition: Zero errors, zero type failures, all tests pass
Output: JSON report to state/pipeline_state.json

### /coverage - Coverage Agent (Gate 2)
Prerequisite: Gate 1 PASS
Runs: pytest --cov with threshold check
Pass condition: Coverage >= minimum threshold (default 80%)
Output: Coverage report, threshold comparison

### /xplat - Cross-Platform Agent (Gate 3)
Prerequisite: Gates 1-2 PASS
Runs: Path checks, env var checks, Windows tests, Ubuntu tests
Pass condition: Identical results on both platforms
Output: Comparison report, OS-specific failures

### /pymatrix - Python Matrix Agent (Gate 4)
Prerequisite: Gates 1-3 PASS
Runs: Tests on Python 3.9, 3.10, 3.11, 3.12, 3.13
Pass condition: All Python versions pass
Output: Per-version results, compatibility report

### /security - Security Agent (Gate 5)
Prerequisite: Gates 1-4 PASS
Runs: Secrets scan, dependency audit, license check
Pass condition: No secrets, no critical vulnerabilities, compatible licenses
Output: Security report

### /api-check - API Compatibility Agent (Gate 6)
Prerequisite: Gates 1-5 PASS
Runs: Extract public API, compare to last release, check deprecations
Pass condition: No unintended breaking changes
Output: API diff report

### /package - Packaging Agent (Gate 7)
Prerequisite: Gates 1-6 PASS
Runs: Validate pyproject.toml, build wheel/sdist, test install, test entry points
Pass condition: Package builds, installs, imports work, all entry points respond
Output: Build artifacts, installation test results

### /ship - Git/PR/Publish Agent (Gate 8)
Prerequisite: ALL gates (1-7) must show PASS
Runs: Diff analysis, commit generation, PR creation, optional PyPI publish
Refuses to run: If ANY prior gate is not PASS

### /plan - Planning Agent (Advisory)
No prerequisites - runs anytime
Runs: Architecture analysis, dependency mapping, complexity scoring
Output: Analysis report, tech debt identification

### /deps - Dependencies Agent (Advisory)
No prerequisites - runs anytime
Runs: Lock file sync, version bounds check, deprecated package scan
Output: Dependency health report

### /full-pipeline - Run All Gates
Runs gates 1-8 in sequence
Stops at first failure
Reports final status

## Handoff Protocol

When passing between gates, current agent writes to state/pipeline_state.json:

```json
{
  "pipeline_id": "uuid",
  "started_at": "ISO8601",
  "current_gate": "coverage",
  "gates": {
    "lint_test": {
      "status": "PASS",
      "started_at": "ISO8601",
      "completed_at": "ISO8601",
      "duration_seconds": 45,
      "details": {
        "lint_errors": 0,
        "type_errors": 0,
        "tests_passed": 142,
        "tests_failed": 0
      }
    }
  }
}
```

On FAIL:
```json
{
  "gate": "cross_platform",
  "status": "FAIL",
  "failure_context": {
    "os": "windows",
    "test": "test_path_handling",
    "file": "src/utils.py",
    "line": 47,
    "error": "Hardcoded forward slash in path"
  }
}
```

## Pre-Gate Verification

Before running any gate except Gate 1, verify prerequisites:

```python
def can_run_gate(gate_name: str, state: dict) -> bool:
    prerequisites = get_prerequisites(gate_name)
    for prereq in prerequisites:
        if state["gates"].get(prereq, {}).get("status") != "PASS":
            return False
    return True
```

## Cross-Platform Checks (Gate 3 Specifics)

MUST validate:
| Check | Rule |
|-------|------|
| Path separators | Use `pathlib.Path` or `os.path.join()` |
| Line endings | All files LF, `.gitattributes` enforces |
| Case sensitivity | No files differing only by case |
| Shell commands | No bash-specific syntax in cross-platform code |
| Temp directories | Use `tempfile` module |
| Home directory | Use `Path.home()` |
| Executable extensions | Handle `.exe` suffix for Windows |

## Python Matrix Checks (Gate 4 Specifics)

MUST validate against ALL declared Python versions:
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

Failure on ANY version blocks the pipeline.

## Package Build Checks (Gate 7 Specifics)

MUST verify:
1. pyproject.toml is valid
2. All required files included in distribution
3. Wheel builds successfully
4. sdist builds successfully
5. Package installs in clean venv
6. All declared imports work
7. All entry points respond to --help
8. README renders correctly (twine check)
9. Version is consistent across all locations

## Response Format

Always report status:
```
GATE: [name]
STATUS: [PASS/FAIL]
DURATION: [seconds]
DETAILS:
  - [item]
NEXT: [next gate or STOP]
```

## File Creation Rules

When creating or editing Python files:
- Use `pathlib.Path` for ALL file operations
- Use `tempfile` for temporary files
- Use `getpass.getuser()` for username
- Use `subprocess.run()` with `shell=False` and list args
- Include type hints on all functions
- Target Python 3.9+ syntax
```

---

## Slash Commands

### .claude/commands/lint.md
```markdown
Run the lint/test agent (Gate 1).

Execute in sequence:
1. `ruff check . --fix` for auto-fixable issues
2. `ruff format .`
3. `mypy . --strict`
4. `pytest -v`

Write results to state/pipeline_state.json with gate name "lint_test".

If any step fails:
- Stop immediately
- Record failure context (file, line, error)
- Do not proceed to next gate
- Report what failed and why
```

### .claude/commands/coverage.md
```markdown
Run the coverage agent (Gate 2).

PREREQUISITE: Verify lint_test gate shows PASS in state/pipeline_state.json.
If not PASS, refuse to run and report: "Gate 1 (Lint/Test) must pass first."

Execute:
1. `pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml`
2. Compare coverage percentage to threshold in config/coverage_rules.yaml
3. Check per-file minimums

Write results to state/pipeline_state.json with gate name "coverage".

If coverage below threshold:
- Report current coverage vs required
- List files below per-file minimum
- FAIL the gate
```

### .claude/commands/xplat.md
```markdown
Run the cross-platform agent (Gate 3).

PREREQUISITE: Verify gates 1-2 show PASS in state/pipeline_state.json.
If any not PASS, refuse to run and list blocking gates.

Execute:
1. Static analysis for cross-platform issues:
   - Path separator check
   - Line ending check
   - Environment variable check
   - Case sensitivity check
   - Shell command check
2. Start Ubuntu container, run full test suite
3. Start Windows container, run full test suite
4. Compare results - must be identical

Write results to state/pipeline_state.json with gate name "cross_platform".

If tests diverge:
- Report which OS failed
- Report specific test failures
- Include file, line, error for each
- FAIL the gate
```

### .claude/commands/pymatrix.md
```markdown
Run the Python version matrix agent (Gate 4).

PREREQUISITE: Verify gates 1-3 show PASS in state/pipeline_state.json.
If any not PASS, refuse to run and list blocking gates.

Execute:
1. Run tests in Python 3.9 container
2. Run tests in Python 3.10 container
3. Run tests in Python 3.11 container
4. Run tests in Python 3.12 container
5. Run tests in Python 3.13 container
6. Compare results - all must pass

Write results to state/pipeline_state.json with gate name "python_matrix".

If any version fails:
- Report which Python version(s) failed
- Report specific failures per version
- FAIL the gate
```

### .claude/commands/security.md
```markdown
Run the security agent (Gate 5).

PREREQUISITE: Verify gates 1-4 show PASS in state/pipeline_state.json.
If any not PASS, refuse to run and list blocking gates.

Execute:
1. `gitleaks detect --source .` for secrets
2. `pip-audit` for dependency vulnerabilities
3. License check against allowed list

Write results to state/pipeline_state.json with gate name "security".

If any security issue found:
- Report type of issue (secret, vulnerability, license)
- Report location and severity
- FAIL the gate for critical/high severity
```

### .claude/commands/api-check.md
```markdown
Run the API compatibility agent (Gate 6).

PREREQUISITE: Verify gates 1-5 show PASS in state/pipeline_state.json.
If any not PASS, refuse to run and list blocking gates.

Execute:
1. Extract current public API (classes, functions, methods)
2. Get baseline API from latest release tag
3. Compare for breaking changes
4. Run tests with `-W error::DeprecationWarning`

Write results to state/pipeline_state.json with gate name "api_compat".

If breaking changes detected:
- List each breaking change (removed, changed signature, etc.)
- Ask developer to confirm if intentional
- FAIL the gate unless explicitly marked as intentional
```

### .claude/commands/package.md
```markdown
Run the packaging agent (Gate 7).

PREREQUISITE: Verify gates 1-6 show PASS in state/pipeline_state.json.
If any not PASS, refuse to run and list blocking gates.

Execute:
1. Validate pyproject.toml schema
2. Check all required files present
3. `python -m build` to create wheel and sdist
4. Create clean virtual environment
5. Install wheel into clean venv
6. Test all imports work
7. Run each entry point with `--help`
8. `twine check dist/*` for README rendering
9. Verify version consistency

Write results to state/pipeline_state.json with gate name "packaging".

If any step fails:
- Report which step failed
- Include specific error
- FAIL the gate
```

### .claude/commands/ship.md
```markdown
Run the git/PR/publish agent (Gate 8).

PREREQUISITE: Verify ALL gates (1-7) show PASS in state/pipeline_state.json.
If ANY gate is not PASS, refuse to run. List all blocking gates.

Execute:
1. Analyze git diff for all changes
2. Generate semantic commit message per commit_conventions.yaml
3. Create detailed PR description including:
   - Summary of changes
   - Test results from all 7 gates
   - Cross-platform confirmation
   - Python version matrix results
   - Coverage report
   - Security scan results
   - API compatibility status
   - Package build confirmation
4. Commit and push
5. Create PR
6. If release requested: tag, create GitHub release, publish to PyPI

NEVER execute if ANY prior gate has not passed.
```

### .claude/commands/plan.md
```markdown
Run the planning agent (advisory, no gate requirements).

Execute:
1. Analyze codebase architecture
2. Map internal dependencies
3. Calculate complexity scores
4. Identify technical debt (TODOs, FIXMEs, high complexity)

Output report with:
- Architecture diagram
- Dependency graph
- Complexity hotspots
- Tech debt inventory
- Recommended improvements
```

### .claude/commands/deps.md
```markdown
Run the dependencies agent (advisory, no gate requirements).

Execute:
1. Check if lock file matches pyproject.toml
2. Analyze version bounds (too loose? too tight?)
3. Check for deprecated packages
4. Check for known conflicts
5. Check for outdated packages

Output report with:
- Lock file sync status
- Version bound warnings
- Deprecated package list
- Conflict warnings
- Update recommendations
```

### .claude/commands/full-pipeline.md
```markdown
Run the complete pipeline (Gates 1-8).

Execute gates in sequence:
1. /lint
2. /coverage
3. /xplat
4. /pymatrix
5. /security
6. /api-check
7. /package
8. /ship (only if all prior gates PASS)

Stop at first failure. Report:
- Which gate failed
- Failure details
- Pipeline stopped at gate N of 8

On full success:
- Report all gates passed
- Confirm code is ready to ship
```

---

## State Schema

### state/pipeline_state.json
```json
{
  "pipeline_id": "550e8400-e29b-41d4-a716-446655440000",
  "started_at": "2024-01-15T10:30:00Z",
  "current_gate": "python_matrix",
  "target_package": "my-package",
  "target_version": "1.2.0",
  "gates": {
    "lint_test": {
      "status": "PASS",
      "started_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:30:45Z",
      "duration_seconds": 45,
      "details": {
        "lint_errors": 0,
        "lint_warnings": 2,
        "type_errors": 0,
        "tests_passed": 142,
        "tests_failed": 0,
        "tests_skipped": 3
      },
      "artifacts": [
        "reports/lint_report.json",
        "reports/test_report.xml"
      ]
    },
    "coverage": {
      "status": "PASS",
      "started_at": "2024-01-15T10:30:46Z",
      "completed_at": "2024-01-15T10:31:30Z",
      "duration_seconds": 44,
      "details": {
        "total_coverage": 87.3,
        "threshold": 80,
        "branch_coverage": 82.1,
        "files_below_minimum": []
      },
      "artifacts": [
        "reports/coverage.xml",
        "htmlcov/index.html"
      ]
    },
    "cross_platform": {
      "status": "PASS",
      "started_at": "2024-01-15T10:31:31Z",
      "completed_at": "2024-01-15T10:35:30Z",
      "duration_seconds": 239,
      "details": {
        "static_checks": {
          "path_issues": 0,
          "line_ending_issues": 0,
          "env_var_issues": 0,
          "case_sensitivity_issues": 0,
          "shell_command_issues": 0
        },
        "environments": {
          "ubuntu-latest": {
            "status": "PASS",
            "tests_passed": 142,
            "tests_failed": 0
          },
          "windows-latest": {
            "status": "PASS",
            "tests_passed": 142,
            "tests_failed": 0
          }
        }
      }
    },
    "python_matrix": {
      "status": "RUNNING",
      "started_at": "2024-01-15T10:35:31Z",
      "completed_at": null,
      "details": {
        "versions": {
          "3.9": {"status": "PASS", "tests_passed": 142, "tests_failed": 0},
          "3.10": {"status": "PASS", "tests_passed": 142, "tests_failed": 0},
          "3.11": {"status": "PASS", "tests_passed": 142, "tests_failed": 0},
          "3.12": {"status": "RUNNING"},
          "3.13": {"status": "PENDING"}
        }
      }
    },
    "security": {
      "status": "PENDING"
    },
    "api_compat": {
      "status": "PENDING"
    },
    "packaging": {
      "status": "PENDING"
    },
    "git_workflow": {
      "status": "PENDING"
    }
  }
}
```

---

## Plugin Manifest

### plugin.json
```json
{
  "name": "claude-code-agents",
  "display_name": "Python Package CI/CD Pipeline",
  "version": "2.0.0",
  "description": "Multi-agent CI/CD pipeline ensuring Python packages pass cross-platform, multi-version, and package build verification before shipping.",
  "author": "Gorombo",
  "license": "MIT",
  "repository": "https://github.com/gorombo/claude-code-agents",
  "homepage": "https://gorombo.com/claude-code-agents",
  
  "claude_code_version": ">=1.0.0",
  
  "entry_points": {
    "commands": ".claude/commands/",
    "main": "scripts/pipeline.py"
  },
  
  "dependencies": {
    "python": ">=3.9",
    "docker": ">=20.0",
    "packages": [
      "ruff>=0.1.0",
      "mypy>=1.0.0",
      "pytest>=7.0.0",
      "pytest-cov>=4.0.0",
      "build>=1.0.0",
      "twine>=4.0.0",
      "pip-audit>=2.0.0",
      "gitleaks>=8.0.0",
      "pyyaml>=6.0.0"
    ]
  },
  
  "gates": [
    {"name": "lint_test", "display": "Lint & Test", "required": true},
    {"name": "coverage", "display": "Coverage", "required": true},
    {"name": "cross_platform", "display": "Cross-Platform", "required": true},
    {"name": "python_matrix", "display": "Python Matrix", "required": true},
    {"name": "security", "display": "Security", "required": true},
    {"name": "api_compat", "display": "API Compatibility", "required": true},
    {"name": "packaging", "display": "Package Build", "required": true},
    {"name": "git_workflow", "display": "Git/PR/Publish", "required": true}
  ],
  
  "commands": [
    {"name": "lint", "gate": 1, "description": "Run linting and tests"},
    {"name": "coverage", "gate": 2, "description": "Check test coverage"},
    {"name": "xplat", "gate": 3, "description": "Cross-platform validation"},
    {"name": "pymatrix", "gate": 4, "description": "Python version matrix"},
    {"name": "security", "gate": 5, "description": "Security audit"},
    {"name": "api-check", "gate": 6, "description": "API compatibility"},
    {"name": "package", "gate": 7, "description": "Package build verification"},
    {"name": "ship", "gate": 8, "description": "Git, PR, and publish"},
    {"name": "plan", "gate": null, "description": "Architecture analysis"},
    {"name": "deps", "gate": null, "description": "Dependency health check"},
    {"name": "full-pipeline", "gate": "all", "description": "Run complete pipeline"}
  ],
  
  "configuration_files": [
    "config/pipeline.yaml",
    "config/lint_rules.yaml",
    "config/coverage_rules.yaml",
    "config/xplat_rules.yaml",
    "config/python_versions.yaml",
    "config/security_rules.yaml",
    "config/api_compat_rules.yaml",
    "config/packaging_rules.yaml",
    "config/dependency_rules.yaml",
    "config/commit_conventions.yaml"
  ],
  
  "docker_required": true,
  "docker_images": [
    "python:3.9-slim",
    "python:3.10-slim",
    "python:3.11-slim",
    "python:3.12-slim",
    "python:3.13-slim"
  ],
  
  "tags": [
    "ci-cd",
    "python",
    "cross-platform",
    "testing",
    "packaging",
    "security",
    "quality"
  ]
}
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Initialize repo with directory structure
- [ ] Create CLAUDE.md with governance rules
- [ ] Create plugin.json manifest
- [ ] Build state_manager.py
- [ ] Build pipeline.py orchestrator skeleton
- [ ] Create all slash command files
- [ ] Create all configuration YAML files
- [ ] Set up basic test fixtures

### Phase 2: Lint/Test Agent (Week 1)
- [ ] Implement run_lint.py (ruff integration)
- [ ] Implement run_format.py (ruff format)
- [ ] Implement run_typecheck.py (mypy)
- [ ] Implement run_tests.py (pytest)
- [ ] Implement agent.py entry point
- [ ] Wire up state reporting
- [ ] Test Gate 1 end-to-end

### Phase 3: Coverage Agent (Week 2)
- [ ] Implement run_coverage.py
- [ ] Implement check_threshold.py
- [ ] Implement generate_report.py
- [ ] Implement agent.py entry point
- [ ] Wire up state reporting
- [ ] Test Gate 2 with prerequisite check

### Phase 4: Cross-Platform Agent (Week 2)
- [ ] Create Dockerfile.ubuntu
- [ ] Create Dockerfile.windows
- [ ] Create docker-compose.yml
- [ ] Implement check_paths.py
- [ ] Implement check_line_endings.py
- [ ] Implement check_env_vars.py
- [ ] Implement check_case_sensitivity.py
- [ ] Implement check_shell_commands.py
- [ ] Implement check_temp_paths.py
- [ ] Implement run_windows_tests.py
- [ ] Implement run_ubuntu_tests.py
- [ ] Implement compare_results.py
- [ ] Implement agent.py entry point
- [ ] Test Gate 3 end-to-end

### Phase 5: Python Matrix Agent (Week 3)
- [ ] Create Dockerfile.py39 through Dockerfile.py313
- [ ] Create docker-compose.matrix.yml
- [ ] Implement run_python3X_tests.py for each version
- [ ] Implement matrix_runner.py
- [ ] Implement compare_results.py
- [ ] Implement agent.py entry point
- [ ] Test Gate 4 end-to-end

### Phase 6: Security Agent (Week 3)
- [ ] Implement scan_secrets.py (gitleaks)
- [ ] Implement audit_deps.py (pip-audit)
- [ ] Implement check_licenses.py
- [ ] Implement agent.py entry point
- [ ] Test Gate 5 end-to-end

### Phase 7: API Compatibility Agent (Week 4)
- [ ] Implement extract_public_api.py
- [ ] Implement compare_api.py
- [ ] Implement check_deprecations.py
- [ ] Implement generate_api_diff.py
- [ ] Implement agent.py entry point
- [ ] Test Gate 6 end-to-end

### Phase 8: Packaging Agent (Week 4)
- [ ] Implement validate_pyproject.py
- [ ] Implement check_manifest.py
- [ ] Implement build_package.py
- [ ] Implement test_install.py
- [ ] Implement test_entry_points.py
- [ ] Implement validate_readme.py
- [ ] Implement check_version.py
- [ ] Implement publish.py
- [ ] Implement agent.py entry point
- [ ] Test Gate 7 end-to-end

### Phase 9: Git Workflow Agent (Week 5)
- [ ] Implement analyze_diff.py
- [ ] Implement generate_commit.py
- [ ] Implement generate_pr.py
- [ ] Implement verify_gates.py
- [ ] Implement publish_release.py
- [ ] Implement agent.py entry point
- [ ] Test Gate 8 end-to-end

### Phase 10: Supporting Agents (Week 5)
- [ ] Implement planning agent scripts
- [ ] Implement documentation agent scripts
- [ ] Implement dependencies agent scripts

### Phase 11: Integration & Hardening (Week 6)
- [ ] Full pipeline integration testing
- [ ] Edge case handling
- [ ] Error recovery procedures
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Marketplace preparation

---

## Testing the Pipeline

### Manual Test Sequence
```bash
# 1. Make a change with a cross-platform issue
echo "config_path = '/home/user/config.yaml'" >> src/config.py

# 2. Run lint (passes - valid Python)
/lint

# 3. Run coverage (passes - if tests exist)
/coverage

# 4. Run xplat (FAILS - hardcoded Unix path)
/xplat

# 5. Try to ship (REFUSES - xplat failed)
/ship

# 6. Fix the issue
# config_path = Path.home() / 'config.yaml'

# 7. Run full pipeline
/full-pipeline
```

### Entry Point Test
```bash
# After Gate 7 package build:
# 1. Clean venv is created
# 2. Wheel is installed
# 3. Each entry point tested:

my-cli-command --help  # Must respond
my-other-command --help  # Must respond

# If any entry point fails to respond, Gate 7 fails
```

---

## Success Criteria

Pipeline is complete when:
- [ ] Code cannot reach GitHub without passing all 8 gates
- [ ] Windows failures caught locally before push
- [ ] Ubuntu failures caught locally before push
- [ ] Python 3.9-3.13 compatibility verified before push
- [ ] Package builds, installs, and entry points verified before push
- [ ] Coverage threshold enforced
- [ ] Security vulnerabilities blocked
- [ ] Breaking API changes detected
- [ ] Failure context is specific (file, line, OS, Python version, error)
- [ ] Developers cannot bypass gates
- [ ] Full pipeline runs in < 15 minutes
- [ ] PR descriptions include all gate confirmations
- [ ] Plugin installable from marketplace
```