# Directory Operations Guide

ollama-prompt supports powerful directory operations that enable efficient codebase analysis. Instead of referencing individual files, you can analyze entire directories with a single reference.

---

## Quick Reference

| Syntax | Operation | Description |
|--------|-----------|-------------|
| `@./dir/` | List | List directory contents |
| `@./dir/:list` | List (explicit) | Same as above |
| `@./dir/:tree` | Tree | Directory tree (depth=3) |
| `@./dir/:search:PATTERN` | Search | Find pattern in files |

---

## Syntax Details

### Directory Listing

```bash
# List contents of src directory
ollama-prompt --prompt "What files are in @./src/?"

# Explicit list operation (same result)
ollama-prompt --prompt "Show contents: @./src/:list"
```

**Output:** File and folder names in the directory.

**Use when:** You need a quick overview of what's in a directory.

---

### Directory Tree

```bash
# Show directory structure (depth=3)
ollama-prompt --prompt "Analyze the architecture: @./src/:tree"
```

**Output:** Hierarchical tree view showing nested structure up to 3 levels deep.

**Use when:**
- Architecture analysis
- Understanding project organization
- Identifying module boundaries
- Reviewing layer separation

**Example Output:**
```
src/
├── api/
│   ├── routes/
│   │   ├── auth.py
│   │   └── users.py
│   └── middleware/
│       └── validation.py
├── models/
│   ├── user.py
│   └── session.py
└── utils/
    └── helpers.py
```

---

### Pattern Search

```bash
# Search for TODO comments
ollama-prompt --prompt "Find incomplete work: @./src/:search:TODO"

# Search for security-sensitive patterns
ollama-prompt --prompt "Security audit: @./src/:search:password"

# Search for function definitions
ollama-prompt --prompt "Find all handlers: @./src/:search:def handle"
```

**Output:** Matching lines with file paths and line numbers.

**Use when:**
- Security audits (find `eval`, `exec`, `password`)
- Code review (find `TODO`, `FIXME`, `HACK`)
- Pattern discovery (find specific functions or classes)
- Refactoring preparation (find all usages)

---

## Use Case Examples

### 1. Architecture Analysis

**Goal:** Understand project structure and design patterns.

```bash
ollama-prompt --prompt "Analyze the architecture of this codebase:

Project Structure:
@./src/:tree

Focus on:
- Layer separation (presentation, business, data)
- Module organization
- Design patterns used
- Coupling between components

Provide recommendations for improvement." \
--model kimi-k2-thinking:cloud
```

**Why this works:** The `:tree` operation gives the model a complete view of how code is organized, enabling meaningful architectural analysis.

---

### 2. Security Audit

**Goal:** Find potential security vulnerabilities.

```bash
ollama-prompt --prompt "Security audit - search for vulnerable patterns:

Dangerous functions:
@./src/:search:eval
@./src/:search:exec
@./src/:search:subprocess.call

Hardcoded secrets:
@./src/:search:password
@./src/:search:api_key
@./src/:search:secret

SQL patterns:
@./src/:search:execute(

For each finding:
1. Assess severity (Critical/High/Medium/Low)
2. Explain the risk
3. Provide remediation" \
--model kimi-k2-thinking:cloud
```

**Why this works:** Multiple `:search:` operations find specific vulnerability patterns across the entire codebase in one prompt.

---

### 3. Code Review

**Goal:** Find issues and incomplete work before PR.

```bash
ollama-prompt --prompt "Pre-PR code review checklist:

Project structure:
@./src/:tree

Find issues:
@./src/:search:TODO
@./src/:search:FIXME
@./src/:search:HACK
@./src/:search:XXX

For each finding:
- Assess if it blocks the PR
- Prioritize by importance
- Suggest resolution" \
--model deepseek-v3.1:671b-cloud
```

**Why this works:** Combines structure overview with targeted issue finding.

---

### 4. Dependency Analysis

**Goal:** Understand import patterns and dependencies.

```bash
ollama-prompt --prompt "Analyze dependencies in this project:

Structure:
@./src/:tree

Import patterns:
@./src/:search:^import
@./src/:search:^from

Identify:
- External dependencies
- Internal module dependencies
- Circular dependency risks
- Unused imports" \
--model kimi-k2-thinking:cloud
```

---

### 5. Test Coverage Analysis

**Goal:** Assess test organization and coverage.

```bash
ollama-prompt --prompt "Test coverage analysis:

Test structure:
@./tests/:tree

Test patterns:
@./tests/:search:def test_
@./tests/:search:@pytest

Source structure:
@./src/:tree

Assess:
- Test organization (mirrors source?)
- Coverage gaps (modules without tests?)
- Test naming conventions
- Missing test types (unit, integration, e2e)" \
--model kimi-k2-thinking:cloud
```

---

## Combining with File References

You can mix directory operations with individual file references:

```bash
ollama-prompt --prompt "Review this authentication module:

Overall structure:
@./src/auth/:tree

Main implementation:
@./src/auth/login.py

Find security patterns:
@./src/auth/:search:password

Provide detailed security review." \
--model kimi-k2-thinking:cloud
```

---

## Token Efficiency

Directory operations are more token-efficient than listing multiple files:

| Approach | Tokens | Coverage |
|----------|--------|----------|
| 10 individual `@./file` refs | ~15,000 | 10 files |
| `@./dir/:tree` | ~500 | Entire structure |
| `@./dir/:search:pattern` | ~1,000 | All matches |

**Recommendation:** Use `:tree` for structure, `:search:` for specific patterns, individual files only for deep analysis.

---

## Best Practices

### Do

- Use `:tree` first to understand structure
- Use `:search:` for targeted pattern finding
- Combine multiple `:search:` operations in one prompt
- Mix directory ops with selective file deep-dives

### Don't

- Don't use `@./dir/` for very large directories (>1000 files)
- Don't search for overly common patterns (e.g., `@./src/:search:the`)
- Don't nest multiple `:tree` operations unnecessarily

---

## Troubleshooting

### "Directory too large"

If a directory is too large, use `:tree` instead of listing, or narrow your search:

```bash
# Instead of: @./src/
# Use: @./src/:tree
# Or: @./src/specific-module/
```

### "No matches found"

Pattern search is case-sensitive. Try variations:

```bash
@./src/:search:TODO
@./src/:search:todo
@./src/:search:Todo
```

### "Truncated output"

For very large results, narrow the scope:

```bash
# Instead of: @./src/:search:import
# Use: @./src/api/:search:import
```

---

## Agent-Specific Usage

### ollama-task-router

The router automatically selects directory operations based on task type:
- Architecture requests → `:tree`
- Security audits → `:search:` patterns
- Code reviews → `:tree` + `:search:TODO`

### ollama-chunked-analyzer

For large directories:
1. First pass with `:tree` for structure
2. Identify key areas
3. Deep dive with individual file refs

### ollama-parallel-orchestrator

Each analysis angle uses optimal operations:

| Angle | Operation | Example |
|-------|-----------|---------|
| Security | `:search:` | `@./src/:search:eval` |
| Architecture | `:tree` | `@./src/:tree` |
| Performance | `:search:` | `@./src/:search:for.*in.*range` |
| Code Quality | `:search:` | `@./src/:search:TODO` |

---

## Requirements

- ollama-prompt v1.1.0 or higher
- Ollama CLI installed and running

---

## See Also

- [README.md](../README.md) - Plugin overview
- [ollama-prompt documentation](https://github.com/dansasser/ollama-prompt)
