# Claude Ollama Agents Plugin - Package Contents

## Overview

Complete production-ready plugin for Claude Code that provides intelligent multi-agent system for delegating analysis, code review, and complex reasoning tasks to local ollama models.

**Version:** 1.0.0
**Release Date:** 2025-01-09
**License:** MIT

## What Gets Installed

### 0. Plugin Manifest → `.claude-plugin/plugin.json`

The plugin manifest defines the plugin metadata and configuration:

**plugin.json** (in .claude-plugin/ directory)
- Plugin name, version, description
- Author information
- License (MIT)
- Keywords and categories
- Component paths (agents, commands)
- Repository and homepage URLs

This file enables the plugin to be recognized by Claude Code's plugin system and can be installed via marketplaces or direct installation.

### 1. Agents (3 files) → `~/.claude/agents/`

Core agent definitions that orchestrate ollama model interactions:

- **ollama-task-router.md** (13.5 KB)
  - Meta-orchestrator that routes tasks to appropriate execution paths
  - Classifies tasks (code/vision/text/analysis)
  - Selects best model based on capabilities
  - Routes to chunked analyzer or parallel orchestrator as needed

- **ollama-chunked-analyzer.md** (6.8 KB)
  - Handles large files exceeding model context windows
  - Automatic token estimation and chunk calculation
  - Intelligent chunking with overlap for context continuity
  - Result synthesis from multiple chunks

- **ollama-parallel-orchestrator.md** (20.2 KB)
  - Deep multi-perspective analysis with parallel execution
  - Decomposes tasks into 2-4 concurrent perspectives
  - Session tracking with unique orchestration IDs
  - Comprehensive synthesis of combined results

### 2. Slash Commands (5 files) → `~/.claude/commands/`

User-facing commands for common operations:

- **analyze.md** (1.7 KB)
  - `/analyze <file> [focus_area]`
  - Quick file analysis with focus on specific areas
  - Focus areas: security, architecture, performance, quality, general

- **review.md** (2.7 KB)
  - `/review <file> [strictness]`
  - Code review with multiple strictness levels
  - Levels: quick, standard, thorough

- **architect.md** (4.0 KB)
  - `/architect <file> [aspect]`
  - Architecture and design pattern analysis
  - Aspects: patterns, scalability, security, dependencies, all

- **models.md** (4.9 KB)
  - `/models [action]`
  - Manage ollama model registry
  - Actions: discover, list, check, defaults

- **deep-analyze.md** (6.0 KB)
  - `/deep-analyze <file> [perspectives]`
  - Multi-perspective deep analysis
  - Perspectives: security, architecture, implementation, testing, performance

### 3. Helper Scripts (7 files) → `~/.claude/scripts/`

Backend utilities that support agent operations:

- **discover-models.sh** (8.4 KB)
  - Scans ollama for installed models
  - Auto-detects capabilities from model metadata
  - Generates fallback lists based on installed models
  - Updates model registry

- **query-model-capabilities.sh** (6.1 KB)
  - Queries individual model capabilities
  - Parses ollama show Capabilities section
  - Maps capabilities to taxonomy (vision, code, reasoning, general)
  - Infers from model name patterns and family

- **check-model.sh** (1.9 KB)
  - Verifies if specific model is available
  - Shows context window size
  - Returns [OK] or [FAIL] status

- **should-chunk.sh** (2.4 KB)
  - Estimates token count from file/directory size
  - Compares to model context window (80% threshold)
  - Recommends chunking or direct analysis
  - Suggests chunk count if needed

- **decompose-task.sh** (5.3 KB)
  - Breaks complex tasks into parallel perspectives
  - Validates perspective count (2-4)
  - Generates unique session IDs
  - Prepares for parallel execution

- **track-sessions.sh** (5.8 KB)
  - Tracks parallel session execution
  - Saves session metadata to registry
  - Updates orchestration state
  - Monitors completion status

- **combine-sessions.sh** (8.9 KB)
  - Loads all sessions for an orchestration
  - Applies combination strategy (synthesis/comparison/summary)
  - Generates comprehensive final report
  - Saves combined results

### 4. Configuration

- **model-capabilities.json** → `~/.claude/model-capabilities.json`
  - Model registry with capabilities
  - User defaults for task types
  - Task preferences with fallback chains
  - Capability inference rules

- **orchestrations/** → `~/.claude/orchestrations/`
  - Session tracking files
  - Orchestration metadata
  - Combined analysis results

### 5. Documentation

- **README.md** (12.1 KB)
  - Complete installation and usage guide
  - All slash command documentation
  - Model selection guidelines
  - Examples and troubleshooting

- **LICENSE** (1.1 KB)
  - MIT License

- **PACKAGE-CONTENTS.md** (this file)
  - Complete package inventory
  - Installation manifest

## Installation Summary

```bash
./install.sh
```

**Installs:**
- 3 agents to ~/.claude/agents/
- 5 slash commands to ~/.claude/commands/
- 7 helper scripts to ~/.claude/scripts/
- 1 model registry to ~/.claude/model-capabilities.json
- Creates ~/.claude/orchestrations/ directory

**Total Files Created:** 16
**Total Disk Space:** ~150 KB

## Prerequisites

1. **ollama** - The ollama application from [ollama.ai](https://ollama.ai)
2. **Models** - Pull models you want to use:
   ```bash
   ollama pull kimi-k2-thinking:cloud
   ollama pull qwen3-vl:235b-instruct-cloud
   ollama pull deepseek-v3.1:671b-cloud
   ```
3. **ollama-prompt** - Python interface: `pip install ollama-prompt`

## Features Summary

### Context Efficiency
- Saves 70%+ of Claude's context budget
- Enables 5-13x more efficient analysis
- Preserves tokens for complex reasoning

### Multi-Model Support
- Automatic model discovery
- Intelligent model selection
- Capability-based routing
- Fallback chains

### Parallel Processing
- Multi-perspective analysis
- Concurrent execution
- Session tracking
- Result synthesis

### Cross-Platform
- Windows compatible (no emojis, proper path handling)
- macOS compatible
- Linux compatible
- Uses Path.home() for all file operations

### Automatic Features
- Chunking detection for large files
- Model capability inference
- Token estimation
- Context window checking

## Usage Examples

```bash
# Quick security check
/review src/auth.py quick

# Deep architecture analysis
/architect src/ all

# Multi-perspective analysis
/deep-analyze implementation-plan.md security,architecture,implementation

# Check available models
/models list

# Discover new models
/models discover

# General file analysis
/analyze README.md
```

## Architecture

```
User Command
    ↓
Slash Command (commands/)
    ↓
Agent (agents/)
    ↓
Helper Scripts (scripts/)
    ↓
Ollama Model
    ↓
Result Synthesis
    ↓
Return to Claude
```

## Model Capabilities System

**Capabilities:**
- `vision`: Image analysis, OCR, screenshots
- `code`: Code review, security, refactoring
- `reasoning`: Multi-step logic, complex analysis
- `general`: General purpose tasks

**Auto-Detection:**
1. Parse ollama show Capabilities section
2. Map to taxonomy (vision→vision, tools→code, thinking→reasoning)
3. Infer from name patterns (coder, thinking, vl, etc.)
4. Infer from model family (kimi, deepseek, qwen)

**Fallback System:**
- Preferred model per task type
- Auto-generated fallback lists
- Based on installed models only
- Capability matching

## Verification

After installation, verify with:

```bash
# Check installation
ls ~/.claude/agents/
ls ~/.claude/commands/
ls ~/.claude/scripts/

# Test model discovery
/models discover

# Check available models
/models list

# Verify a slash command
/analyze ~/.claude/README.md
```

## Support

**Issues:** Open a GitHub issue
**Documentation:** See README.md
**Workflow Guide:** See CLAUDE.md (if available)

## Credits

Created for Claude Code by Daniel T Sasser II
Part of the SIM-ONE Framework ecosystem

---

**Package Version:** 1.0.0
**Generated:** 2025-01-09
**Complete and ready for distribution**
