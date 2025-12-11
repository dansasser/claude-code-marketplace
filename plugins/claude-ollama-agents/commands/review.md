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
   - Directory: Use directory operations for efficient review
   - Large codebase: Focus on changed files or critical paths

2. **Directory Operations for Reviews:**

   When reviewing directories, use these operations:

   | Strictness | Directory Operations | Purpose |
   |------------|---------------------|---------|
   | quick | `@./dir/:search:TODO` | Find obvious issues |
   | standard | `@./dir/:tree` + `@./dir/:search:FIXME` | Structure + known issues |
   | thorough | `@./dir/:tree` + multiple `:search:` patterns | Full analysis |

   **Example Directory Review Prompts:**

   Quick: `@./src/:search:TODO` + `@./src/:search:FIXME`
   Standard: `@./src/:tree` + `@./src/:search:TODO` + `@./src/:search:HACK`
   Thorough: `@./src/:tree` + security patterns + quality patterns

3. **Select Review Strategy:**

   **Quick Review:**
   Invoke ollama-task-router agent:
   - Request: Quick code review focusing on critical bugs and security
   - Target: $1
   - For directories: Use `@./dir/:search:` for obvious issues
   - Agent handles model selection and execution

   **Standard Review:**
   Invoke ollama-task-router agent:
   - Request: Standard code review
   - Checklist: Security, quality, bugs, performance, best practices
   - Target: $1
   - For directories: Use `@./dir/:tree` for structure + `:search:` for issues

   **Thorough Review:**
   Invoke ollama-parallel-orchestrator agent:
   - Perspectives: security, quality, architecture, testing
   - Target: $1
   - For directories: Each perspective uses appropriate directory operations
   - Multi-angle comprehensive analysis

4. **Review Checklist (for agent to cover):**
   - Security: Injection, XSS, auth issues, secrets in code
   - Quality: Naming, structure, complexity, duplication
   - Bugs: Logic errors, edge cases, error handling
   - Performance: Inefficient algorithms, memory leaks
   - Best Practices: Language idioms, design patterns
   - Testing: Test coverage, test quality

5. **Your Role:**
   - Invoke appropriate agent based on strictness level
   - Receive agent's analysis
   - Format results for user
   - Prioritize findings by severity

6. **Report Format:**
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

7. **Priority Levels:**
   - CRITICAL: Security vulnerabilities, data loss risks
   - MAJOR: Bugs, performance issues, maintainability problems
   - MINOR: Style issues, minor optimizations

**Directory Review Benefits:**
- `@./dir/:tree` shows full project structure in ~500 tokens
- `@./dir/:search:TODO` finds all incomplete work instantly
- `@./dir/:search:FIXME` locates known issues across codebase
- More comprehensive than reviewing files individually

**Remember:** Agents handle the heavy analysis. You orchestrate and present results clearly.
