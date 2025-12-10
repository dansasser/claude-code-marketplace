# TODO: Directory Operations Support

**Project Directory:** C:\Claude\repos\claude-code-marketplace\plugins\claude-ollama-agents
**Branch:** feature/ollama-prompt-directory-support
**Date Created:** 2025-12-10
**Last Updated:** 2025-12-10

---

## Current Context

Integrating ollama-prompt's new directory operation capabilities into the claude-ollama-agents plugin. This enables agents to reference entire directories instead of individual files, improving analysis efficiency.

**New Syntax:**
- `@./dir/` - List directory contents
- `@./dir/:tree` - Directory tree (depth=3)
- `@./dir/:search:PATTERN` - Search for pattern

---

## Tasks

### Phase 1: Documentation Foundation

- [ ] **1.1 Create docs/directory-operations.md**
  - Syntax reference table
  - When to use each operation
  - Examples for each use case
  - Best practices
  - Token efficiency comparisons

- [ ] **1.2 Update README.md**
  - Add "Directory Operations" section after "Features"
  - Update feature list
  - Add examples
  - Link to detailed docs

---

### Phase 2: Agent Core Updates

- [ ] **2.1 Update agents/ollama-task-router.md**
  - Add directory detection in routing logic
  - Add "Directory-Aware Routing" section
  - Add directory-specific model selection guidance
  - Add examples using `@./dir/:tree` and `@./dir/:search:`
  - Update decision matrix for directory targets

- [ ] **2.2 Update agents/ollama-chunked-analyzer.md**
  - Add "Directory Chunking Strategy" section
  - Show when to use `:tree` vs `:list` vs individual files
  - Update workflow to handle directory inputs
  - Add structure-first analysis pattern

- [ ] **2.3 Update agents/ollama-parallel-orchestrator.md**
  - Add "Angle-Specific Directory Operations" section
  - Update angle prompts to use appropriate operations:
    - Security: `@./dir/:search:eval` patterns
    - Architecture: `@./dir/:tree` for structure
    - Performance: `@./dir/:search:loop` patterns
    - Quality: `@./dir/:search:TODO` for incomplete work
  - Update Phase 1 decomposition examples

---

### Phase 3: Command Updates

- [ ] **3.1 Update commands/analyze.md**
  - Add directory analysis workflow
  - Show `@./dir/:tree` for initial structure analysis
  - Add focus area to directory operation mapping
  - Update examples section

- [ ] **3.2 Update commands/review.md**
  - Add "Directory Review Strategy" section
  - Quick review: `@./dir/:list` + key files
  - Standard review: `@./dir/:tree` + targeted analysis
  - Thorough review: `@./dir/:tree` + `@./dir/:search:FIXME`
  - Update examples

- [ ] **3.3 Update commands/architect.md**
  - Make `@./dir/:tree` the primary input
  - Add pattern search for architectural patterns
  - Show layer identification from tree output
  - Update "Understand Scope" section

- [ ] **3.4 Update commands/deep-analyze.md**
  - Add "Directory Operations per Perspective" section
  - Update perspective-specific recommendations
  - Add directory operation examples

---

### Phase 4: Script Enhancements

- [ ] **4.1 Update scripts/decompose-task.sh**
  - Generate `@./` directory references in scope output
  - Add `directory_op` field to angle JSON output
  - Add angle-specific directory operation suggestions
  - Update scope generation for directories

- [ ] **4.2 Update scripts/should-chunk.sh**
  - Add directory-specific recommendations
  - Suggest `:tree` for large directories
  - Calculate tokens for directory operations
  - Add recommendations in output

---

### Phase 5: Testing and Validation

- [ ] **5.1 Test slash commands**
  - Test `/analyze src/` with directory
  - Test `/review src/ thorough` with directory
  - Test `/architect src/` with directory
  - Test `/deep-analyze src/` with directory

- [ ] **5.2 Validate agent behavior**
  - Verify task-router detects directories
  - Verify chunked-analyzer handles directories
  - Verify parallel-orchestrator uses angle-specific ops

- [ ] **5.3 Regression testing**
  - Verify single-file workflows still work
  - Verify existing examples still work

---

### Phase 6: Documentation Finalization

- [ ] **6.1 Update plugin.json**
  - Bump version to 1.1.0
  - Update description if needed

- [ ] **6.2 Finalize CHANGELOG.md**
  - Move Unreleased to version 1.1.0
  - Add release date
  - Review all entries

- [ ] **6.3 Final review**
  - Review all changed files
  - Check for consistency
  - Verify all examples work

- [ ] **6.4 Commit and push**
  - Stage all changes
  - Create commit with detailed message
  - Push to feature branch

---

## File Checklist

| File | Status | Notes |
|------|--------|-------|
| `docs/directory-operations.md` | [ ] New | Reference guide |
| `docs/IMPLEMENTATION-PLAN-directory-support.md` | [x] Done | Planning doc |
| `docs/TODO-directory-support.md` | [x] Done | This file |
| `CHANGELOG.md` | [x] Created | Needs version update |
| `README.md` | [ ] Pending | Add directory section |
| `agents/ollama-task-router.md` | [ ] Pending | Directory routing |
| `agents/ollama-chunked-analyzer.md` | [ ] Pending | Directory chunking |
| `agents/ollama-parallel-orchestrator.md` | [ ] Pending | Angle-specific ops |
| `commands/analyze.md` | [ ] Pending | Directory workflow |
| `commands/review.md` | [ ] Pending | Directory patterns |
| `commands/architect.md` | [ ] Pending | Tree primary |
| `commands/deep-analyze.md` | [ ] Pending | Perspective ops |
| `scripts/decompose-task.sh` | [ ] Pending | Directory refs |
| `scripts/should-chunk.sh` | [ ] Pending | Directory recs |
| `.claude-plugin/plugin.json` | [ ] Pending | Version bump |

---

## Quick Reference: Directory Syntax

```bash
# List directory contents
@./src/
@./src/:list

# Directory tree (depth=3)
@./src/:tree

# Search for pattern
@./src/:search:TODO
@./src/:search:password
@./src/:search:eval
```

---

## Notes

- Minimum ollama-prompt version: v1.1.0
- All changes are additive (backward compatible)
- Focus on architecture (`:tree`) and security (`:search:`) use cases
- Tree depth is fixed at 3 levels
