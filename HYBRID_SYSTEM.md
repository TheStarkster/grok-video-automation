# Hybrid Workflow System

## Overview

The Hybrid Workflow System combines AI intelligence with fast deterministic execution:

1. **First Run**: AI agent learns the workflow (uses tokens)
2. **Subsequent Runs**: Fast recorded script (no tokens needed!)
3. **Auto-Recovery**: Falls back to AI if UI changes

## 🚀 Quick Start

### Option 1: Hybrid Runner (Recommended)

```bash
# First run: AI learns and records workflow
python test_hybrid_runner.py

# Second run: Uses recorded script (super fast, no tokens!)
python test_hybrid_runner.py

# Force AI mode (ignore recorded script)
python hybrid_runner.py --force-ai
```

### Option 2: Direct AI Agent (Always uses AI)

```bash
python test_langgraph_agent.py
```

### Option 3: Run Recorded Script Only

```bash
# After workflow is recorded
python workflows/grok_video_workflow_script.py
```

## 📁 Generated Files

After first successful run, you'll get:

```
workflows/
├── grok_video_workflow.json          # Workflow metadata
└── grok_video_workflow_script.py     # Standalone Python script
```

## 💡 How It Works

### AI Agent Mode (First Run)
- Uses GPT-4 vision + LangGraph
- Analyzes screenshots and DOM
- Adapts to UI changes
- Records successful steps
- **Cost**: ~$0.10-0.50 per run (depends on iterations)

### Recorded Script Mode (Subsequent Runs)
- Direct Selenium commands
- No AI inference
- 10-20x faster execution
- **Cost**: $0.00 (no API calls!)

### Fallback Logic
```python
if recorded_script_exists():
    try:
        run_recorded_script()  # Fast path
    except Exception:
        run_ai_agent()  # Smart recovery
else:
    run_ai_agent()  # Learn first time
```

## 🎯 Use Cases

### Perfect For:
- **Repetitive tasks** on stable UIs
- **Production automation** with cost optimization
- **CI/CD pipelines** needing speed + reliability

### AI Agent Fallback Helps When:
- Website UI changes
- New elements appear
- Workflow variations needed
- Error recovery required

## 📊 Performance Comparison

| Mode | Speed | Cost | Adaptability |
|------|-------|------|--------------|
| Recorded Script | ⚡⚡⚡ 10-30s | 💰 $0 | ❌ Fixed workflow |
| AI Agent | ⚡ 60-120s | 💰💰💰 $0.10-0.50 | ✅ Fully adaptive |
| Hybrid | ⚡⚡⚡ → ⚡ | 💰 $0 → 💰💰💰 | ✅ Best of both |

## 🔧 Customization

### Create Custom Workflow

```python
from hybrid_runner import HybridRunner

runner = HybridRunner(workflow_name="my_custom_workflow")

task = """
1. Navigate to website
2. Click button X
3. Type text Y
4. Download result
"""

runner.run(task, initial_url="https://example.com")
```

### Workflow Recorder API

```python
from workflow_recorder import WorkflowRecorder

recorder = WorkflowRecorder("my_workflow")

# Save workflow
recorder.save_workflow(action_history, task, success=True)

# Check if exists
if recorder.workflow_exists():
    info = recorder.get_workflow_info()
    print(f"Workflow has {info['total_steps']} steps")
```

## 🛠️ Advanced Usage

### Force Regenerate Workflow

```bash
# Delete existing workflow
rm -rf workflows/grok_video_workflow*

# Run to regenerate
python test_hybrid_runner.py
```

### Multiple Workflows

```python
# Create different workflows
video_runner = HybridRunner("grok_video_workflow")
image_runner = HybridRunner("grok_image_workflow")
chat_runner = HybridRunner("grok_chat_workflow")
```

### Headless Mode

```bash
# Run recorded script in headless mode
python workflows/grok_video_workflow_script.py --headless
```

## 🎓 Best Practices

1. **First Run**: Use AI agent to learn workflow
2. **Verify**: Check generated script works correctly
3. **Production**: Use hybrid runner for cost optimization
4. **Monitor**: Watch for script failures (indicates UI changes)
5. **Update**: Let AI re-learn when UI changes

## 🐛 Troubleshooting

### Script Fails Every Time
- UI might have changed
- Run with `--force-ai` to re-learn
- Check `workflows/*.json` for recorded steps

### AI Agent Slow
- Normal! First run learns the workflow
- Subsequent runs use fast script
- Patience pays off with token savings

### Script Works Sometimes
- Timing issues (add delays in generated script)
- Dynamic content (AI agent handles this better)
- Consider using hybrid mode always

## 💰 Cost Analysis

Example: Running 100 times

- **AI Only**: 100 runs × $0.20 = **$20.00**
- **Hybrid**: 1 AI run ($0.20) + 99 script runs ($0) = **$0.20**
- **Savings**: **$19.80 (99% reduction!)**

## 🔮 Future Enhancements

- [ ] Auto-detect UI changes
- [ ] Multiple workflow variants
- [ ] Parallel execution
- [ ] Web dashboard
- [ ] Workflow marketplace

