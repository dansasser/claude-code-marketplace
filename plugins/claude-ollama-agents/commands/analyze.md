# Analyze File or Directory with Ollama

Analyze the specified file or directory using the ollama agent pipeline.

**Usage:** `/analyze <file_or_directory> [focus_area]`

**Examples:**
- `/analyze src/auth.py security` - Security analysis of single file
- `/analyze README.md` - General analysis
- `/analyze src/ architecture` - Architecture analysis of directory
- `/analyze src/ security` - Security audit of entire directory

---

You are an intelligent task router for ollama-based analysis.

**Task:** Analyze the target at path: $1
**Focus Area:** $2

**Your Process:**

1. **Check Target:**
   - Determine if target is file or directory
   - For files: Get size and estimate tokens
   - For directories: Use directory operations for efficiency

2. **Select Strategy:**

   **For Files:**
   - Small files (< 20KB): Direct ollama-prompt
   - Large files (> 20KB): Use ollama-chunked-analyzer approach

   **For Directories:**
   - Architecture focus: Use `@./dir/:tree` for structure analysis
   - Security focus: Use `@./dir/:search:PATTERN` for vulnerability patterns
   - Quality focus: Use `@./dir/:search:TODO` + `@./dir/:tree`
   - General: Use `@./dir/:tree` then targeted analysis

3. **Directory Operations by Focus Area:**

   | Focus Area | Primary Operation | Example |
   |------------|-------------------|---------|
   | security | `@./dir/:search:` | `@./src/:search:eval`, `@./src/:search:password` |
   | architecture | `@./dir/:tree` | `@./src/:tree` |
   | performance | `@./dir/:search:` | `@./src/:search:for.*in`, `@./src/:search:query` |
   | quality | `@./dir/:search:` + `:tree` | `@./src/:search:TODO`, `@./src/:tree` |
   | general | `@./dir/:tree` | `@./src/:tree` |

4. **Invoke Agent:**
   Use the Task tool to invoke the ollama-task-router agent:
   - Pass the target path: $1
   - Pass the focus area: $2
   - Agent uses appropriate directory operations
   - Agent handles model selection and execution

5. **Agent Will:**
   - Detect if target is file or directory
   - Select appropriate model (kimi-k2-thinking, deepseek, qwen3-vl)
   - Use directory operations for directories
   - Route to chunked analyzer if needed
   - Execute analysis with ollama-prompt
   - Return synthesized results

6. **Your Role:**
   - Receive agent's analysis report
   - Present findings to user concisely
   - Highlight critical issues
   - Provide actionable recommendations

**Focus Areas:**
- security: Vulnerabilities, attack vectors, security best practices
- architecture: Design patterns, scalability, maintainability
- performance: Bottlenecks, optimization opportunities
- quality: Code quality, best practices, refactoring needs
- general: Comprehensive overview

**Directory Analysis Benefits:**
- `@./dir/:tree` uses ~500 tokens vs ~15,000 for reading files individually
- `@./dir/:search:PATTERN` finds specific issues across entire codebase
- More efficient and comprehensive than file-by-file analysis

**Remember:** This delegates to ollama to save your context budget!
