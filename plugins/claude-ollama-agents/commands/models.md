# Manage Ollama Models

Discover, list, and manage ollama models for the agent pipeline.

**Usage:** `/models [action] [target]`

**Actions:**
- `discover`: Scan and register all installed ollama models
- `list`: Show all registered models and capabilities
- `check <model>`: Verify specific model availability
- `defaults`: Show default models for each task type

**Examples:**
- `/models discover` - Scan for new models
- `/models list` - Show all models
- `/models check kimi-k2-thinking:cloud` - Check if model available
- `/models defaults` - Show default selections

---

You are managing the ollama model registry.

**Action:** ${1:-list}
**Target:** $2

**Your Process:**

1. **Execute Action:**

   **Discover:**
   ```bash
   # Scan ollama and update registry
   ~/.claude/scripts/discover-models.sh

   # Show results
   cat ~/.claude/model-capabilities.json | python3 -c "
   import json, sys
   data = json.load(sys.stdin)
   print(f'Discovered {len(data[\"models\"])} models:')
   for model, info in data['models'].items():
       caps = ', '.join(set(info['capabilities']))
       print(f'  - {model}: {caps}')
   "
   ```

   **List:**
   ```bash
   # Show all models with capabilities
   cat ~/.claude/model-capabilities.json | python3 -c "
   import json, sys
   from pathlib import Path

   registry_file = Path.home() / '.claude' / 'model-capabilities.json'
   with open(registry_file, 'r', encoding='utf-8') as f:
       data = json.load(f)

   print('## Registered Models\n')
   for model, info in sorted(data['models'].items()):
       caps = ', '.join(set(info['capabilities']))
       family = info.get('family', 'unknown')
       context = info.get('context_window', 'unknown')
       cost = info.get('cost', 'unknown')

       print(f'### {model}')
       print(f'  - Family: {family}')
       print(f'  - Capabilities: {caps}')
       if isinstance(context, int):
           print(f'  - Context: {context:,} tokens')
       else:
           print(f'  - Context: {context}')
       print(f'  - Cost: {cost}')
       print()
   "
   ```

   **Check:**
   ```bash
   # Check if specific model is available
   ~/.claude/scripts/check-model.sh $2
   ```

   **Defaults:**
   ```bash
   # Show default model selections
   cat ~/.claude/model-capabilities.json | python3 -c "
   import json, sys
   from pathlib import Path

   registry_file = Path.home() / '.claude' / 'model-capabilities.json'
   with open(registry_file, 'r', encoding='utf-8') as f:
       data = json.load(f)

   print('## Default Models by Task\n')
   defaults = data.get('user_defaults', {})
   for task, model in sorted(defaults.items()):
       print(f'- **{task}**: {model}')

   print('\n## Task Preferences with Fallbacks\n')
   prefs = data.get('task_preferences', {})
   for task, config in sorted(prefs.items()):
       if config.get('preferred'):
           print(f'### {task}')
           print(f'  Preferred: {config[\"preferred\"][0]}')
           if config.get('fallback'):
               fallbacks = config['fallback'][:3]
               print(f'  Fallbacks: {\" -> \".join(fallbacks)}')
           print()
   "
   ```

2. **Model Capability Reference:**

   **Vision Models:**
   - qwen3-vl:235b-instruct-cloud (best vision, 262K context)
   - qwen3:1.7b (lightweight, has vision)

   **Code Models:**
   - kimi-k2-thinking:cloud (reasoning + code, 262K context)
   - deepseek-v3.1:671b-cloud (strong code, 163K context)
   - qwen2.5-coder:3b (lightweight coder)

   **Reasoning Models:**
   - kimi-k2-thinking:cloud (explicit thinking)
   - deepseek-v3.1:671b-cloud (strong reasoning)

   **General Purpose:**
   - All models have general capability
   - Prefer larger models for complex tasks

3. **Registry Location:**
   - File: `~/.claude/model-capabilities.json`
   - Contains: Models, capabilities, defaults, task preferences
   - Auto-updated: By discover-models.sh

4. **Capability Taxonomy:**
   - `vision`: Image analysis, OCR, screenshots
   - `code`: Code review, refactoring, security
   - `reasoning`: Multi-step logic, complex analysis
   - `general`: General purpose tasks

**Common Operations:**

```bash
# After installing new ollama model
/models discover

# Before using specific model
/models check deepseek-v3.1:671b-cloud

# See what's available
/models list

# Check your defaults
/models defaults
```

**Registry Structure:**
```json
{
  "models": {
    "model-name": {
      "capabilities": ["code", "reasoning"],
      "context_window": 128000,
      "family": "deepseek",
      "cost": "cloud"
    }
  },
  "user_defaults": {
    "code": "kimi-k2-thinking:cloud",
    "vision": "qwen3-vl:235b-instruct-cloud"
  },
  "task_preferences": {
    "code": {
      "preferred": ["kimi-k2-thinking:cloud"],
      "fallback": ["deepseek-v3.1:671b-cloud", ...]
    }
  }
}
```

**Remember:** Keep your model registry up to date for best agent performance!
