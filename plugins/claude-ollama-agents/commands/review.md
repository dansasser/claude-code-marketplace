# Code Review with Ollama

Perform comprehensive code review using ollama agents.

**Usage:** `/review <file_or_directory> [strictness]`

**Strictness Levels:**
- `quick`: Fast review, major issues only
- `standard`: Balanced review (default)
- `thorough`: Deep analysis with security, quality, and architecture

**Examples:**
- `/review src/auth.py` - Standard review of auth module
- `/review src/api/ thorough` - Deep review of API directory
- `/review main.py quick` - Quick check

---

You are performing a code review by orchestrating ollama agents.

**Target:** $1
**Strictness:** ${2:-standard}

**Your Process:**

1. **Determine Scope:**
   - Single file: Direct analysis via ollama-task-router
   - Directory: Review key files (main entry points, complex modules)
   - Large codebase: Focus on changed files or critical paths

2. **Select Review Strategy:**

   **Quick Review:**
   Invoke ollama-task-router agent:
   - Request: Quick code review focusing on critical bugs and security
   - Target: $1
   - Agent handles model selection and execution

   **Standard Review:**
   Invoke ollama-task-router agent:
   - Request: Standard code review
   - Checklist: Security, quality, bugs, performance, best practices
   - Target: $1

   **Thorough Review:**
   Invoke ollama-parallel-orchestrator agent:
   - Perspectives: security, quality, architecture, testing
   - Target: $1
   - Multi-angle comprehensive analysis

3. **Review Checklist (for agent to cover):**
   - Security: Injection, XSS, auth issues, secrets in code
   - Quality: Naming, structure, complexity, duplication
   - Bugs: Logic errors, edge cases, error handling
   - Performance: Inefficient algorithms, memory leaks
   - Best Practices: Language idioms, design patterns
   - Testing: Test coverage, test quality

4. **Your Role:**
   - Invoke appropriate agent based on strictness level
   - Receive agent's analysis
   - Format results for user
   - Prioritize findings by severity

5. **Report Format:**
   ```
   ## Code Review Summary

   **File/Directory:** $1
   **Strictness:** ${2:-standard}

   ### Critical Issues (Fix Immediately)
   - [From agent analysis]

   ### Major Issues (Fix Soon)
   - [From agent analysis]

   ### Minor Issues (Consider Fixing)
   - [From agent analysis]

   ### Positive Observations
   - [From agent analysis]

   ### Recommendations
   - [Actionable items]
   ```

6. **Priority Levels:**
   - CRITICAL: Security vulnerabilities, data loss risks
   - MAJOR: Bugs, performance issues, maintainability problems
   - MINOR: Style issues, minor optimizations

**Remember:** Agents handle the heavy analysis. You orchestrate and present results clearly.
