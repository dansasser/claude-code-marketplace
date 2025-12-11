# Implementation Plan: ollama-prompt Directory Support Integration

**Branch:** `feature/ollama-prompt-directory-support`
**Created:** 2025-12-10
**Author:** Claude Code (with Daniel T Sasser II)
**Status:** In Progress

---

## Executive Summary

This plan integrates ollama-prompt's new directory operation capabilities (`@./dir/`, `@./dir/:tree`, `@./dir/:search:PATTERN`) into the claude-ollama-agents plugin. These features enable more efficient codebase analysis by allowing agents to reference entire directories instead of individual files.

---

## Background

### Current State

The claude-ollama-agents plugin currently uses ollama-prompt with single-file references only:
- `@./file.py` - Reference individual files
- Multiple `@./file1.py @./file2.py` - List multiple files explicitly

### New Capabilities (ollama-prompt v1.1.0+)

| Syntax | Operation | Use Case |
|--------|-----------|----------|
| `@./dir/` | List directory contents | Quick directory overview |
| `@./dir/:list` | Explicit list operation | Same as above, explicit |
| `@./dir/:tree` | Directory tree (depth=3) | Architecture/structure analysis |
| `@./dir/:search:PATTERN` | Search for pattern | Security audits, finding TODOs |

### Benefits

1. **Reduced Prompt Complexity** - Reference 1 directory vs listing 20 files
2. **Better Context** - Model sees full structure, not isolated files
3. **Targeted Analysis** - Search operations find specific patterns across codebase
4. **Architecture Awareness** - Tree view shows module organization

---

## Scope

### In Scope

1. **Agent Updates** (3 files)
   - `agents/ollama-chunked-analyzer.md`
   - `agents/ollama-task-router.md`
   - `agents/ollama-parallel-orchestrator.md`

2. **Command Updates** (4 files)
   - `commands/analyze.md`
   - `commands/review.md`
   - `commands/architect.md`
   - `commands/deep-analyze.md`

3. **Script Updates** (2 files)
   - `scripts/decompose-task.sh`
   - `scripts/should-chunk.sh`

4. **Documentation Updates**
   - `README.md` - Add directory operations section
   - New: `docs/directory-operations.md` - Detailed guide

### Out of Scope

- Changes to ollama-prompt itself
- New slash commands
- Breaking changes to existing workflows

---

## Implementation Phases

### Phase 1: Documentation Foundation

**Goal:** Create reference documentation for directory operations

**Tasks:**
1. Create `docs/directory-operations.md` with:
   - Syntax reference table
   - When to use each operation
   - Examples for each use case
   - Best practices

2. Update `README.md`:
   - Add "Directory Operations" section
   - Link to detailed docs
   - Update feature list

**Deliverables:**
- [ ] `docs/directory-operations.md`
- [ ] Updated `README.md`

---

### Phase 2: Agent Core Updates

**Goal:** Update agent definitions with directory-aware capabilities

#### 2.1 ollama-task-router.md

**Changes:**
- Add directory detection in routing logic
- Add directory-specific model selection guidance
- Add examples using `@./dir/:tree` and `@./dir/:search:`

**Key Additions:**
```markdown
### Directory-Aware Routing

When target is a directory:
- Architecture analysis: Use `@./dir/:tree` for structure overview
- Security audit: Use `@./dir/:search:PATTERN` for vulnerability patterns
- Code review: Use `@./dir/:list` then targeted file analysis
```

#### 2.2 ollama-chunked-analyzer.md

**Changes:**
- Add directory chunking strategies
- Show when to use `:tree` vs `:list` vs individual files
- Update workflow to handle directory inputs

**Key Additions:**
```markdown
### Directory Chunking Strategy

For directory analysis:
1. First pass: `@./dir/:tree` for structure (low tokens)
2. Identify key areas from tree output
3. Deep dive with `@./subdir/:search:PATTERN` or individual files
```

#### 2.3 ollama-parallel-orchestrator.md

**Changes:**
- Update angle-specific prompts to use appropriate directory operations
- Security angle: `@./dir/:search:eval` patterns
- Architecture angle: `@./dir/:tree` for structure
- Quality angle: `@./dir/:search:TODO` for incomplete work

**Key Additions:**
```markdown
### Angle-Specific Directory Operations

| Angle | Recommended Operation | Example |
|-------|----------------------|---------|
| Security | `:search:PATTERN` | `@./src/:search:eval` |
| Architecture | `:tree` | `@./src/:tree` |
| Performance | `:search:PATTERN` | `@./src/:search:loop` |
| Code Quality | `:search:PATTERN` | `@./src/:search:TODO` |
```

**Deliverables:**
- [ ] Updated `agents/ollama-task-router.md`
- [ ] Updated `agents/ollama-chunked-analyzer.md`
- [ ] Updated `agents/ollama-parallel-orchestrator.md`

---

### Phase 3: Command Updates

**Goal:** Update slash commands to leverage directory operations

#### 3.1 commands/analyze.md

**Changes:**
- Add directory analysis workflow
- Show `@./dir/:tree` for initial structure analysis
- Add focus area to directory operation mapping

#### 3.2 commands/review.md

**Changes:**
- Add directory review patterns
- Quick review: `@./dir/:list` + key files
- Thorough review: `@./dir/:tree` + `@./dir/:search:FIXME`

#### 3.3 commands/architect.md

**Changes:**
- Make `@./dir/:tree` the primary input for architecture analysis
- Add pattern search for architectural patterns
- Show layer identification from tree output

#### 3.4 commands/deep-analyze.md

**Changes:**
- Update perspective-specific operations
- Add directory operation recommendations per perspective

**Deliverables:**
- [ ] Updated `commands/analyze.md`
- [ ] Updated `commands/review.md`
- [ ] Updated `commands/architect.md`
- [ ] Updated `commands/deep-analyze.md`

---

### Phase 4: Script Enhancements

**Goal:** Update helper scripts for directory awareness

#### 4.1 scripts/decompose-task.sh

**Changes:**
- Generate `@./` directory references in scope output
- Add angle-specific directory operation suggestions
- Output directory operation type per angle

**Example Output Enhancement:**
```json
{
  "angles": [
    {
      "name": "Security",
      "scope": "@./src/auth/",
      "directory_op": ":search:password|secret|key",
      "model": "kimi-k2-thinking:cloud"
    }
  ]
}
```

#### 4.2 scripts/should-chunk.sh

**Changes:**
- Add directory-specific recommendations
- Suggest `:tree` for structure-first analysis of large directories
- Calculate tokens for directory listing vs tree vs full read

**Deliverables:**
- [ ] Updated `scripts/decompose-task.sh`
- [ ] Updated `scripts/should-chunk.sh`

---

### Phase 5: Testing and Validation

**Goal:** Verify all updates work correctly

**Test Cases:**
1. `/analyze src/` - Should use directory operations
2. `/review src/ thorough` - Should use tree + search
3. `/architect src/` - Should use tree primarily
4. `/deep-analyze src/` - Should use angle-specific ops

**Validation Checklist:**
- [ ] All agents parse directory syntax correctly
- [ ] Routing logic handles directories appropriately
- [ ] Commands produce expected prompts
- [ ] Scripts generate valid `@./` references
- [ ] No regressions in single-file workflows

---

### Phase 6: Documentation Finalization

**Goal:** Complete all documentation updates

**Tasks:**
- [ ] Update CHANGELOG.md
- [ ] Update version in plugin.json
- [ ] Review all examples for consistency
- [ ] Add migration notes if needed

---

## File Change Summary

| File | Change Type | Priority |
|------|-------------|----------|
| `docs/directory-operations.md` | New | High |
| `README.md` | Update | High |
| `agents/ollama-task-router.md` | Update | High |
| `agents/ollama-chunked-analyzer.md` | Update | High |
| `agents/ollama-parallel-orchestrator.md` | Update | High |
| `commands/analyze.md` | Update | Medium |
| `commands/review.md` | Update | Medium |
| `commands/architect.md` | Update | Medium |
| `commands/deep-analyze.md` | Update | Medium |
| `scripts/decompose-task.sh` | Update | Medium |
| `scripts/should-chunk.sh` | Update | Medium |
| `CHANGELOG.md` | Update | High |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing workflows | Low | High | Maintain backward compatibility, add not replace |
| Directory ops not supported in older ollama-prompt | Medium | Medium | Document minimum version requirement |
| Large directories cause token overflow | Medium | Medium | Add size warnings, recommend chunking |

---

## Success Criteria

1. All agents can intelligently use directory operations
2. Commands provide clear directory analysis workflows
3. Documentation is complete and accurate
4. No regressions in existing functionality
5. Token efficiency improved for directory analysis

---

## Timeline

| Phase | Estimated Effort | Dependencies |
|-------|-----------------|--------------|
| Phase 1: Documentation | 1 hour | None |
| Phase 2: Agent Updates | 2 hours | Phase 1 |
| Phase 3: Command Updates | 1.5 hours | Phase 2 |
| Phase 4: Script Updates | 1 hour | Phase 2 |
| Phase 5: Testing | 1 hour | Phases 2-4 |
| Phase 6: Finalization | 0.5 hours | Phase 5 |

**Total Estimated:** ~7 hours

---

## Appendix: Directory Operation Examples

### Architecture Analysis
```bash
ollama-prompt --prompt "Analyze the architecture of this codebase:

Structure:
@./src/:tree

Focus on:
- Layer separation (presentation, business, data)
- Module dependencies
- Design patterns used
- Coupling between components" --model kimi-k2-thinking:cloud
```

### Security Audit
```bash
ollama-prompt --prompt "Security audit - search for vulnerable patterns:

Dangerous functions:
@./src/:search:eval
@./src/:search:exec
@./src/:search:subprocess

Hardcoded secrets:
@./src/:search:password
@./src/:search:api_key
@./src/:search:secret

Analyze each finding for exploitability." --model kimi-k2-thinking:cloud
```

### Code Review
```bash
ollama-prompt --prompt "Code review checklist:

Project structure:
@./src/:tree

Find issues:
@./src/:search:TODO
@./src/:search:FIXME
@./src/:search:HACK

Provide prioritized list of issues to address." --model deepseek-v3.1:671b-cloud
```
