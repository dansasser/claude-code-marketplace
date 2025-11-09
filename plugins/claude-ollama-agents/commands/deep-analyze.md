# Deep Multi-Perspective Analysis

Comprehensive analysis using parallel orchestrator with multiple perspectives.

**Usage:** `/deep-analyze <file> [perspectives]`

**Perspectives:** (comma-separated, max 4)
- `security`: Security vulnerabilities and threat modeling
- `architecture`: Design patterns and structural analysis
- `implementation`: Code quality and best practices
- `testing`: Test coverage and validation strategies
- `performance`: Bottlenecks and optimization opportunities

**Examples:**
- `/deep-analyze implementation-plan.md` - Auto-select perspectives
- `/deep-analyze src/auth.py security,testing` - Focus on security and testing
- `/deep-analyze architecture.md architecture,scalability` - Architecture focused

---

You are performing deep multi-perspective analysis using the parallel orchestrator agent.

**Target:** $1
**Perspectives:** ${2:-auto}

**Your Process:**

1. **Validate Target:**
   - Verify file/directory exists (use Read/Glob tools)
   - Check size and estimate tokens
   - Ensure suitable for deep analysis (not trivial files)

2. **Determine Perspectives:**

   **Auto-Select (if perspectives=$ARGUMENTS or empty):**
   Based on file type:
   - Code files (.py, .js, .ts, etc.): security, quality, testing
   - Architecture docs: architecture, scalability, security
   - Implementation plans: security, architecture, implementation
   - API specs: security, architecture, performance

   **User-Specified:**
   Parse comma-separated list from $2
   Validate 2-4 perspectives

3. **Invoke Parallel Orchestrator Agent:**

   Use Task tool to invoke ollama-parallel-orchestrator:
   - Target file: $1
   - Perspectives: Parsed list (2-4 perspectives)
   - Agent will:
     * Decompose into parallel analyses
     * Execute concurrently
     * Track sessions
     * Synthesize results

4. **Perspectives Explained:**

   **Security:**
   - Vulnerabilities and attack vectors
   - Threat modeling
   - Authentication/authorization
   - Input validation
   - Secrets management

   **Architecture:**
   - Design patterns
   - Structural organization
   - Separation of concerns
   - Modularity and coupling
   - Scalability considerations

   **Implementation:**
   - Code quality and readability
   - Best practices adherence
   - Error handling
   - Edge case coverage
   - Refactoring opportunities

   **Testing:**
   - Test coverage assessment
   - Testing strategy
   - Edge cases and corner cases
   - Integration points
   - Test quality

   **Performance:**
   - Bottleneck identification
   - Algorithm efficiency
   - Resource utilization
   - Caching opportunities
   - Optimization recommendations

5. **Your Role:**
   - Invoke ollama-parallel-orchestrator agent via Task tool
   - Receive comprehensive synthesized analysis
   - Format report for user
   - Highlight critical findings
   - Present prioritized recommendations

6. **Expected Report Format (from agent):**
   ```
   # Deep Analysis Report

   **Target:** $1
   **Perspectives:** [list]
   **Orchestration ID:** [id]

   ## Executive Summary
   [High-level summary across all perspectives]

   ## Critical Findings
   ### Security Critical
   - [Issues requiring immediate attention]

   ### Architecture Critical
   - [Structural issues with major impact]

   ### Implementation Critical
   - [Code quality issues needing urgent fix]

   ## Analysis by Perspective
   [Detailed findings from each perspective]

   ## Cross-Perspective Insights
   [Common themes and patterns]

   ## Prioritized Recommendations
   1. [Highest priority]
   2. [Second priority]
   ...

   ## Next Steps
   [Actionable items]
   ```

7. **Session Tracking:**
   - Agent saves results to `~/.claude/orchestrations/[id].json`
   - Session includes all perspective analyses
   - Synthesis strategy applied
   - Full audit trail maintained

**When to Use Deep Analysis:**
- Comprehensive code reviews
- Architecture decision making
- Security audits
- Pre-production validation
- Complex refactoring planning
- Technical debt assessment

**When NOT to Use:**
- Simple file reviews (use `/analyze` instead)
- Quick checks (use `/review quick`)
- Small files < 100 lines
- Trivial changes

**Token Efficiency:**
- Deep analysis delegates to ollama-parallel-orchestrator
- Saves ~70% of Claude's context
- Enables multiple comprehensive analyses per session
- Parallel execution faster than sequential

**Remember:** This invokes the most comprehensive analysis. The parallel orchestrator handles all complexity. You just present the synthesized results clearly.
