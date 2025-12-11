# Changelog

All notable changes to the claude-ollama-agents plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2025-12-10

### Added
- **Directory Operations Support** - Agents now leverage ollama-prompt's directory capabilities
  - `@./dir/` - List directory contents
  - `@./dir/:tree` - Directory tree view (depth=3)
  - `@./dir/:search:PATTERN` - Search for patterns across directory
- New documentation: `docs/directory-operations.md` - Comprehensive guide to directory operations
- Angle-specific directory operations in parallel orchestrator:
  - Security angle: Uses `:search:` for vulnerability patterns
  - Architecture angle: Uses `:tree` for structure analysis
  - Code Quality angle: Uses `:search:` for TODO/FIXME detection

### Changed
- **ollama-task-router.md** - Added directory-aware routing logic
  - Detects directory targets and selects appropriate operations
  - Routes architecture requests to use `:tree` operation
  - Routes security audits to use `:search:` operation
- **ollama-chunked-analyzer.md** - Added directory chunking strategies
  - Structure-first analysis using `:tree` before deep dive
  - Smart chunking based on directory size
- **ollama-parallel-orchestrator.md** - Enhanced angle decomposition
  - Each perspective now uses optimal directory operation
  - Improved parallel execution with directory-aware scopes
- **commands/analyze.md** - Added directory analysis workflow
- **commands/review.md** - Added directory review patterns
- **commands/architect.md** - Made `:tree` primary for architecture analysis
- **commands/deep-analyze.md** - Added perspective-specific directory operations
- **scripts/decompose-task.sh** - Generates `@./` directory references
- **scripts/should-chunk.sh** - Added directory-specific recommendations

### Fixed
- (None in this release)

### Deprecated
- (None in this release)

### Removed
- (None in this release)

### Security
- (None in this release)

---

## [1.0.1] - 2025-01-09

### Changed
- Renamed plugin from `claude-ollama-agents` to `ollama-agents`
- Updated version to 1.0.1

---

## [1.0.0] - 2025-01-09

### Added
- Initial release of claude-ollama-agents plugin
- **Slash Commands:**
  - `/analyze` - File analysis with automatic model selection
  - `/review` - Code review with strictness levels (quick, standard, thorough)
  - `/architect` - Architecture analysis and design patterns
  - `/models` - Model management and discovery
  - `/deep-analyze` - Multi-perspective deep analysis
- **Agents:**
  - `ollama-task-router` - Meta-orchestrator for intelligent task routing
  - `ollama-chunked-analyzer` - Large file handling with automatic chunking
  - `ollama-parallel-orchestrator` - Multi-perspective parallel analysis
- **Helper Scripts:**
  - `discover-models.sh` - Automatic model discovery
  - `query-model-capabilities.sh` - Query model capabilities
  - `check-model.sh` - Verify model availability
  - `should-chunk.sh` - Chunking decision logic
  - `decompose-task.sh` - Task decomposition for parallel analysis
  - `track-sessions.sh` - Session tracking for orchestration
  - `combine-sessions.sh` - Result synthesis
- **Features:**
  - Multi-model support with auto-discovery
  - Context-efficient delegation (saves 70%+ of Claude's context)
  - Parallel analysis with 2.7x speedup
  - Cross-platform compatibility (Windows/macOS/Linux)
  - Automatic chunking for large files
  - Session continuity across chunks

### Technical Details
- Model Registry: `~/.claude/model-capabilities.json`
- Orchestration Directory: `~/.claude/orchestrations/`
- Supported Models: kimi-k2-thinking, qwen3-vl, deepseek-v3.1, qwen2.5-coder

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| 1.1.0 | 2025-12-10 | Directory operations support |
| 1.0.1 | 2025-01-09 | Rename and version update |
| 1.0.0 | 2025-01-09 | Initial release |

---

## Upgrade Notes

### Upgrading to Directory Operations (v1.1.0)

**Minimum Requirements:**
- ollama-prompt v1.1.0 or higher (for directory syntax support)

**Backward Compatibility:**
- All existing single-file workflows continue to work unchanged
- Directory operations are additive, not replacing existing functionality

**New Capabilities:**
- Use `@./src/:tree` instead of listing files manually
- Use `@./src/:search:TODO` to find patterns across codebase
- Architecture analysis now shows full project structure

**Migration (Optional):**
If you have custom prompts using multiple file references like:
```bash
@./src/auth.py @./src/login.py @./src/session.py
```

Consider updating to:
```bash
@./src/:tree  # For structure overview
# or
@./src/auth/:search:def  # For finding functions
```
