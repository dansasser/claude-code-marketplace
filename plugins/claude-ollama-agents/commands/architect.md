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
   - Read architecture documentation if available
   - Identify key components and modules (via Glob/Grep)
   - Map dependencies and relationships

2. **Invoke Appropriate Agent:**

   **Specific Aspect Analysis:**
   Use ollama-task-router agent with focused prompt:
   - Target: $1
   - Aspect: ${2:-all}
   - Request specific analysis (patterns, scalability, security, dependencies)

   **Comprehensive Analysis (aspect=all):**
   Use ollama-parallel-orchestrator agent:
   - Perspectives: architecture, security, scalability, maintainability
   - Target: $1
   - Multi-angle deep analysis

3. **Analysis Framework (for agent to apply):**

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

4. **Your Role:**
   - Invoke appropriate agent based on aspect
   - Receive architectural analysis
   - Format findings for user
   - Highlight key insights and recommendations

5. **Report Format:**
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

**Remember:** Delegate deep architectural analysis to agents. You focus on presenting clear, actionable insights.
