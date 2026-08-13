---
name: colab-cli
description: Provision Google Colab cloud runtimes, execute remote Python scripts and notebooks, manage files, open SSH sessions, and run compute tasks directly from the terminal via the official Google Colab CLI. Use when running code on Google Colab GPUs/TPUs, provisioning remote environments, streaming outputs, or using colab-cli in agentic workflows.
---

<colab-cli>

Google Colab CLI (`google-colab-cli`) is the official Google tool for controlling Colab cloud runtimes directly from the local terminal and agentic environments. It allows provisioning GPUs/TPUs, running Python scripts and Jupyter notebooks remotely with real-time output streaming, managing remote files, port-forwarding web interfaces, and managing session lifecycles without opening a browser.

### Topics Covered
- **Use [Installation-and-Auth]** for installing the official package and authenticating sessions.
- **Use [Runtime-Management]** for provisioning, listing, and stopping GPU/TPU instances.
- **Use [Execution-Modes]** for ephemeral (`run`), persistent (`exec`), and interactive (`ssh`/`repl`) execution.
- **Use [File-and-Data-Transfer]** for uploading datasets, downloading artifacts, and mounting Google Drive.
- **Use [Port-Forwarding-and-Web-UIs]** to tunnel remote TensorBoard, Gradio, and web endpoints locally.
- **Use [Agent-Automation-Patterns]** for headless scripts, cleanup traps, and automated agent pipelines.
- **Use [Anti-Patterns-and-Common-Mistakes]** to avoid unexpected costs, path errors, and credential traps.
- **Use [Examples]** for end-to-end practical workflows.
- **Use [Connecting-Skills]** to understand ecosystem interactions.
- Reference [Command Reference](references/command-reference.md) and [Agent Workflows](references/agent-workflows.md) for complete flag documentation.

</colab-cli>

<Installation-and-Auth>

### Package Installation
Always install the official `google-colab-cli` package (not legacy third-party packages):

```bash
# Recommended installation via uv
uv tool install google-colab-cli

# Alternative via pip
pip install google-colab-cli
```

### Authentication
Authenticate your terminal before launching compute instances:
```bash
# Interactive browser OAuth2 login
colab auth login

# Headless / GCP Application Default Credentials
colab auth login --auth=adc

# Verify active login status
colab auth status
```

</Installation-and-Auth>

<Runtime-Management>

Colab CLI supports two runtime lifecycle patterns: **Persistent Sessions** and **Ephemeral Execution**.

### 1. Persistent Sessions (`colab new` & `colab stop`)
Use when you need to upload datasets, run multiple scripts sequentially, or keep variables in memory.

```bash
# Provision session with a specific GPU accelerator (T4, L4, A100, H100)
colab new --session exp-01 --gpu T4

# Provision with TPU (v2-8, v3-8, v5e1) and high RAM
colab new --session tpu-exp --tpu v5e1 --ram high

# List active sessions and compute status
colab list

# Stop session immediately to release billable resources
colab stop exp-01
```

### 2. Ephemeral Execution (`colab run`)
Automatically provisions a fresh runtime, executes the script/notebook, streams stdout/stderr, and deallocates upon exit:

```bash
# Provision, run, and auto-terminate
colab run --gpu T4 train_model.py
```

</Runtime-Management>

<Execution-Modes>

| Mode | Command | Behavior | When to Use |
|---|---|---|---|
| **Ephemeral Run** | `colab run --gpu T4 script.py` | Starts VM, runs script, streams output, terminates VM | Batch jobs, CI/CD, one-off evaluations |
| **Session Exec** | `colab exec -s <session> -f script.py` | Runs script inside existing session; preserves state | Iterative experiments, multi-step runs |
| **Interactive SSH** | `colab ssh -s <session>` | Opens WebSocket-based interactive shell in `/content` | Debugging, inspecting files, terminal tools |
| **Interactive REPL** | `colab repl -s <session>` | Interactive Python REPL connected to Jupyter kernel | Probing model weights, exploring variables |

### Shebang Usage
Make scripts self-executing on Colab GPUs by adding a shebang:
```python
#!/usr/bin/env -S colab run --gpu T4
import torch
print("GPU:", torch.cuda.get_device_name(0))
```

</Execution-Modes>

<File-and-Data-Transfer>

The remote working root directory is always `/content`.

```bash
# Upload local code / data to remote instance
colab upload -s my-session ./data /content/data

# Download remote model checkpoints / logs to local machine
colab download -s my-session /content/checkpoint.pt ./checkpoints/

# List remote files
colab ls -s my-session /content

# Mount Google Drive into /content/drive
colab drivemount -s my-session
```

</File-and-Data-Transfer>

<Port-Forwarding-and-Web-UIs>

Forward remote services (TensorBoard, Gradio, Streamlit, FastAPI) to your local machine:

```bash
# Forward Gradio (7860) or Streamlit (8501)
colab port-forward -s my-session 7860:7860

# Forward TensorBoard (6006)
colab port-forward -s my-session 6006:6006
```

Access the service locally at `http://localhost:<port>`.

</Port-Forwarding-and-Web-UIs>

<Agent-Automation-Patterns>

When running unattended agent tasks, ensure robust lifecycle management:

1. **Prefer `colab run` for atomic tasks**: Handles spin-up and teardown automatically.
2. **Use Bash Exit Traps for persistent sessions**: Prevents idle GPU usage if an error occurs.

```bash
#!/usr/bin/env bash
set -euo pipefail
SESSION="agent-task-$(date +%s)"
trap "colab stop $SESSION || true" EXIT

colab new -s "$SESSION" --gpu T4
colab upload -s "$SESSION" ./src /content/src
colab exec -s "$SESSION" "python /content/src/evaluate.py"
colab download -s "$SESSION" /content/results.json ./results.json
```

3. **Check Exit Codes**: `colab run` and `colab exec` pass through the remote script exit status. Inspect `$?` to detect remote failures.

</Agent-Automation-Patterns>

<Connecting-Skills>

- **Prerequisites**: Use `coding-principles` to ensure clean script design before cloud execution.
- **Companions**: Use `code-as-tools` to structure modular, notebook-compatible experimentation tools before dispatching them to remote Colab runtimes.
- **Successors**: Use `manage-skills` when updating or extending this skill's capabilities.

</Connecting-Skills>

<Anti-Patterns-and-Common-Mistakes>

| Anti-Pattern | Root Cause / Risk | Correct Approach |
|---|---|---|
| Installing `colab-cli` instead of `google-colab-cli` | Unofficial or outdated community package | Always install `google-colab-cli` via `uv` or `pip` |
| Leaving persistent sessions running indefinitely | Incurring compute charges or exhausting quota | Always run `colab stop <session>` or use `trap` / `colab run` |
| Assuming local relative paths exist on remote | Remote environment has `/content` root | Always upload files first and reference `/content/<path>` |
| Storing credentials inside code | Security leak | Use `colab auth login` or pass secrets via environment variables |
| Launching heavy training with no output checkpoints | Network disconnect loses work | Regularly save checkpoints to `/content/` or Google Drive |

</Anti-Patterns-and-Common-Mistakes>

<Examples>

### Complete End-to-End Evaluation Workflow

```bash
# 1. Verify authentication
colab auth status

# 2. Provision a T4 GPU session
colab new --session model-eval --gpu T4

# 3. Upload project source code
colab upload -s model-eval ./src /content/src

# 4. Install dependencies and run script
colab exec -s model-eval "pip install -q transformers torch && python /content/src/eval.py --output /content/eval_metrics.json"

# 5. Download evaluation metrics locally
colab download -s model-eval /content/eval_metrics.json ./eval_metrics.json

# 6. Deallocate session immediately
colab stop model-eval
```

</Examples>

<References>

- Consult [Command Reference](references/command-reference.md) for full argument lists, GPU/TPU accelerator flags, and options.
- Consult [Agent Workflows](references/agent-workflows.md) for automated pipeline recipes and fault-tolerant agent execution templates.

</References>
