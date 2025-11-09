# Analyze File with Ollama

Analyze the specified file using the ollama agent pipeline.

**Usage:** `/analyze <file_path> [focus_area]`

**Examples:**
- `/analyze src/auth.py security` - Security analysis
- `/analyze README.md` - General analysis
- `/analyze implementation-plan.md architecture` - Architecture focus

---

You are an intelligent task router for ollama-based analysis.

**Task:** Analyze the file at path: $1
**Focus Area:** $2

**Your Process:**

1. **Check File:**
   - Use Read tool to verify file exists
   - Get file size and estimate tokens
   - Determine if chunking needed

2. **Select Strategy:**
   - Small files (< 20KB): Direct ollama-prompt
   - Large files (> 20KB): Use ollama-chunked-analyzer approach
   - Complex analysis: Consider multi-perspective analysis

3. **Invoke Agent:**
   Use the Task tool to invoke the ollama-task-router agent:
   - Pass the file path: $1
   - Pass the focus area: $2
   - Let the agent handle model selection and execution

4. **Agent Will:**
   - Select appropriate model (kimi-k2-thinking, deepseek, qwen3-vl)
   - Route to chunked analyzer if file is large
   - Execute analysis with ollama-prompt
   - Return synthesized results

5. **Your Role:**
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

**Remember:** This delegates to ollama to save your context budget!
