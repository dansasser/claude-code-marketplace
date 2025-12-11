# Architecture Analysis with Ollama

Analyze system architecture, design patterns, and structural decisions.

**Usage:** `/architect <file_or_directory> [aspect]`

**Aspects:**
- `patterns`: Design patterns and architectural patterns
- `scalability`: Scalability analysis
- `security`: Security architecture
- `dependencies`: Dependency analysis
- `all`: Comprehensive architecture review (default)

**Examples:**
- `/architect src/` - Full architecture analysis
- `/architect docs/architecture.md patterns` - Pattern analysis
- `/architect src/api/ scalability` - Scalability review

---

You are performing architecture analysis by orchestrating ollama agents.

**Target:** $1
**Aspect:** ${2:-all}

**Your Process:**

1. **Understand Scope:**
   - Check if target is file or directory
   - For directories: Use `@./dir/:tree` as PRIMARY input for architecture analysis
   - Read architecture documentation if available
   - Map dependencies and relationships

2. **Directory Operations for Architecture:**

   **Architecture analysis is IDEAL for directory operations:**

   | Aspect | Primary Operation | Purpose |
   |--------|-------------------|---------|
   | all | `@./dir/:tree` | Full structure overview |
   | patterns | `@./dir/:tree` + `@./dir/:search:class` | Structure + class patterns |
   | scalability | `@./dir/:tree` | Module organization |
   | security | `@./dir/:tree` + `@./dir/:search:auth` | Security boundaries |
   | dependencies | `@./dir/:search:import` | Import analysis |

   **Example Architecture Prompt:**
   ```bash
   ollama-prompt --prompt "Architecture analysis:

   Project Structure:
   @./src/:tree

   Import Dependencies:
   @./src/:search:^import
   @./src/:search:^from

   Analyze:
   - Layer separation
   - Module boundaries
   - Design patterns
   - Coupling and cohesion"
   ```

3. **Invoke Appropriate Agent:**

   **Specific Aspect Analysis:**
   Use ollama-task-router agent with focused prompt:
   - Target: $1
   - Aspect: ${2:-all}
   - For directories: Agent uses `@./dir/:tree` for structure
   - Request specific analysis (patterns, scalability, security, dependencies)

   **Comprehensive Analysis (aspect=all):**
   Use ollama-parallel-orchestrator agent:
   - Perspectives: architecture, security, scalability, maintainability
   - Target: $1
   - Each perspective uses appropriate directory operations
   - Multi-angle deep analysis

4. **Analysis Framework (for agent to apply):**

   **Structure:**
   - Separation of Concerns: Are responsibilities clearly separated?
   - Modularity: Are modules cohesive and loosely coupled?
   - Layering: Is there clear layering (presentation, business, data)?
   - Abstraction: Are abstractions at appropriate levels?

   **Quality Attributes:**
   - Scalability: Can system handle growth?
   - Maintainability: Is code easy to modify?
   - Testability: Can components be tested independently?
   - Security: Are security principles followed?
   - Performance: Are performance requirements met?

   **Design Principles:**
   - SOLID principles
   - DRY (Don't Repeat Yourself)
   - YAGNI (You Aren't Gonna Need It)
   - KISS (Keep It Simple)

5. **Your Role:**
   - Invoke appropriate agent based on aspect
   - Receive architectural analysis
   - Format findings for user
   - Highlight key insights and recommendations

6. **Report Format:**
   ```
   ## Architecture Analysis

   **Target:** $1
   **Aspect:** ${2:-all}

   ### Architecture Overview
   - High-level structure
   - Key components
   - Design patterns identified

   ### Strengths
   - What's working well
   - Good architectural decisions

   ### Concerns
   - Architectural issues
   - Anti-patterns found
   - Technical debt

   ### Recommendations
   - Specific improvements
   - Refactoring suggestions
   - Pattern applications
   ```

**Why Tree View is Essential for Architecture:**
- Shows complete module hierarchy in ~500 tokens
- Reveals layer separation (or lack thereof)
- Exposes coupling through directory structure
- Identifies module boundaries instantly

**Remember:** Delegate deep architectural analysis to agents. You focus on presenting clear, actionable insights.
