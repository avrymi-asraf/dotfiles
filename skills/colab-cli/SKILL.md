---
name: colab-cli
description: Provision Google Colab cloud runtimes, manage secrets/credentials, execute remote Python scripts and notebooks, manage files, open SSH sessions, and run compute tasks directly from the terminal via the official Google Colab CLI. Use when running code on Google Colab GPUs/TPUs, managing Colab secrets, provisioning remote environments, streaming outputs, or using colab-cli in agentic workflows.
---

<colab-cli>

Google Colab CLI (`google-colab-cli`) connects local terminals and autonomous agents directly to Google Colab cloud runtimes. It enables allocating CPU, GPU (T4, L4, G4, A100, H100), or TPU (v5e1, v6e1) instances, managing secrets via Colab `userdata`, exploring data interactively, executing Python scripts/notebooks remotely with real-time output streaming, transferring files, and managing VM lifecycles without opening a browser.

### Topics Covered
- **Use [Installation-and-Auth]** for installing `google-colab-cli` and configuring ADC / OAuth2 scopes.
- **Use [Runtime-Management]** for provisioning (`new`), listing (`sessions`), inspecting (`status`), and stopping sessions.
- **Use [Interactive-Exploration]** for interactive data probing via REPL, console shell, and Colab web UI attachment (`url`).
- **Use [Execution-Modes]** for ephemeral jobs (`run`), persistent kernel execution (`exec`), and shebang scripts.
- **Use [File-and-Package-Management]** for transferring datasets, editing remote files (`edit`), and installing packages (`install`).
- **Use [Colab-Secrets-and-Credentials]** for accessing Colab userdata secrets (`google.colab.userdata`) and syncing keys into `os.environ`.
- **Use [Colab-Notebook-Bootstrapping]** for self-cloning, secret loading, and setting up repository dependencies in Colab kernels.
- **Use [Agent-Automation-Patterns]** for headless scripts, stdout/stderr streams, error codes, and session isolation.
- **Use [Anti-Patterns-and-Common-Mistakes]** to avoid auth traps, scope errors, missing secrets, and idle resource costs.
- **Use [Examples]** for practical, end-to-end interactive and batch recipes.
- Reference [Command Reference](references/command-reference.md), [Secrets Guide](references/secrets-and-credentials.md), and [Agent Workflows](references/agent-workflows.md) for full details.

</colab-cli>

<Installation-and-Auth>

### Package Installation
```bash
# Recommended installation via uv
uv tool install google-colab-cli
```

### Authentication Strategies
The CLI supports two authentication modes via the global flag `--auth={adc,oauth2}` (default is `adc`).

1. **Application Default Credentials (ADC) — Recommended for Headless & Agents**:
   Log in once with `gcloud` providing the 4 required Colab scopes:
   ```bash
   gcloud auth application-default login \
     --scopes=openid,\
   https://www.googleapis.com/auth/cloud-platform,\
   https://www.googleapis.com/auth/userinfo.email,\
   https://www.googleapis.com/auth/colaboratory
   ```
   - `userinfo.email`: Required for session backend (`colab.research.google.com`).
   - `colaboratory`: Required for keep-alive RPCs (`colab.pa.googleapis.com`).

2. **Verify Auth**:
   - `colab sessions`: Read-only check for server connectivity.
   - `colab whoami`: Displays active email, audience, scopes, and token expiration.

> [!NOTE]
> `colab auth` is for injecting *VM-side* GCP credentials into the running kernel for BigQuery/GCS. It is **not** used to authenticate the local CLI itself.

</Installation-and-Auth>

<Runtime-Management>

### 1. Persistent Session Management (`colab new` / `colab stop`)
Maintains runtime state and kernel memory across multiple commands:
```bash
# Provision named session (always specify -s to avoid random IDs)
colab new -s explore --gpu T4
# Provision with TPU
colab new -s tpu-run --tpu v5e1
# List active sessions and prune stale backend records
colab sessions
# Show hardware, memory, and kernel status
colab status -s explore
# Restart Jupyter kernel while keeping the VM allocated
colab restart-kernel -s explore
# Stop and release VM resources
colab stop -s explore
```
Supported accelerators: `--gpu` (`T4`, `L4`, `G4`, `A100`, `H100`), `--tpu` (`v5e1`, `v6e1`).

### 2. Ephemeral Job Runner (`colab run`)
Provisions a fresh VM, runs the script/notebook, streams output, and automatically terminates the VM:
```bash
colab run --gpu T4 train.py
```

</Runtime-Management>

<Interactive-Exploration>

Colab CLI bridges autonomous agents and human researchers across two complementary modalities:
- **For Agents (CLI/REPL Execution)**: `colab exec` and `colab repl` provide the fastest, headless vehicle to execute cells, inspect persistent in-memory variables, stream logs, and verify code directly on cloud GPUs without browser overhead.
- **For Humans (Visual Web Notebooks)**: `colab url -s <name> --open` connects the browser Web UI directly to that same persistent VM and kernel, allowing humans to visually inspect interactive HTML diffs, markdown narrative, and tables.
- **Interactive Probing Modes**:
  - **Interactive Python REPL (`colab repl`)**: Live Python shell on remote VM keeping variables/data in kernel memory: `colab repl -s explore --output-image ./plot.png`
  - **Remote Shell Console (`colab console`)**: Interactive tmux/bash session in `/content`: `colab console -s explore`
  - **Attach Colab Web Notebook (`colab url`)**: Connects browser UI directly to the CLI VM: `colab url -s explore --open`
  - **Step-by-Step Code Probing (`colab exec`)**: Runs code/scripts against persistent kernel memory: `echo "print(len(dataset))" | colab exec -s explore`

</Interactive-Exploration>

<Execution-Modes>

| Mode | Command | Behavior |
|---|---|---|
| **Ephemeral Run** | `colab run --gpu T4 script.py [args]` | Full lifecycle: new VM → execute → teardown |
| **Session Exec** | `colab exec -s <name> -f script.py` | Transmits local file to remote kernel; keeps state |
| **Piped Exec** | `echo "print(1)" \| colab exec -s <name>` | Executes piped code on remote kernel |
| **Notebook Exec** | `colab exec -s <name> -f notebook.ipynb` | Runs cells, writes output to `notebook_output.ipynb` |
| **Shell Console** | `colab console -s <name>` | Raw interactive TTY / tmux shell on remote VM |
| **Interactive REPL** | `colab repl -s <name>` | Python REPL on remote kernel |

</Execution-Modes>

<File-and-Package-Management>

Working directory on remote VMs is always `/content`.

```bash
# Install packages using high-performance uv inside VM
colab install -s explore torch transformers datasets
colab install -s explore -r requirements.txt
# Upload local files or directories
colab upload -s explore ./local_dir /content/remote_dir
# Download remote artifacts or checkpoints
colab download -s explore /content/checkpoint.pt ./checkpoints/
# List and delete remote files
colab ls -s explore /content
colab rm -s explore /content/temp_data.csv
```

</File-and-Package-Management>

<Colab-Secrets-and-Credentials>

### Accessing Colab Secrets (`google.colab.userdata`)

Google Colab provides a secure key store via the **🔑 Secrets** tab in the notebook UI. In Python, secrets are read with `google.colab.userdata.get('KEY_NAME')`.

Because third-party libraries (`huggingface_hub`, `litellm`, `openai`, `wandb`) look for API keys in `os.environ`, automatically sync Colab secrets into `os.environ` during initialization:

```python
import os
import sys

# Auto-sync Colab Secrets to os.environ
try:
    from google.colab import userdata
    for key in ["HF_TOKEN", "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "WANDB_API_KEY"]:
        try:
            val = userdata.get(key)
            if val and key not in os.environ:
                os.environ[key] = val
        except Exception:
            pass
except ImportError:
    pass  # Local workspace - environment variables or .env will be used
```

**Key Secret Names:**
- `HF_TOKEN`: Hugging Face Hub write/read token for datasets and models.
- `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`: Generator/Auditor LLM API keys.
- `WANDB_API_KEY`: Weights & Biases logging token.

Reference [Secrets Guide](references/secrets-and-credentials.md) for permission error handling and CLI patterns.

</Colab-Secrets-and-Credentials>

<Colab-Notebook-Bootstrapping>

### Self-Bootstrapping with Secrets & Repository Setup

When a notebook is opened in Colab, include this combined bootstrap & secrets cell at the top:

```python
import os
import sys

# 1. Detect Colab environment
IN_COLAB = "google.colab" in sys.modules or os.path.exists("/content")

if IN_COLAB:
    print("🚀 Running on Google Colab. Setting up repository and secrets...")
    REPO_DIR = "/content/<repo-name>"
    if not os.path.exists(REPO_DIR):
        !git clone https://github.com/<owner>/<repo-name>.git {REPO_DIR}
    %cd {REPO_DIR}
    !pip install -q -e .
    if REPO_DIR not in sys.path:
        sys.path.insert(0, REPO_DIR)
    
    # 2. Sync Colab Secrets to os.environ
    try:
        from google.colab import userdata
        for k in ["HF_TOKEN", "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "WANDB_API_KEY"]:
            try:
                val = userdata.get(k)
                if val and k not in os.environ:
                    os.environ[k] = val
            except Exception:
                pass
        print("🔑 Colab secrets loaded into os.environ.")
    except ImportError:
        pass
    print("✅ Environment ready!")
else:
    print("💻 Running in local workspace.")
```

</Colab-Notebook-Bootstrapping>

<Agent-Automation-Patterns>

1. **Stream Separation**: `colab run` logs CLI status to **stderr** and program output to **stdout**:
   ```bash
   colab run --gpu T4 eval.py > output.json 2> run.log
   ```
2. **Exit Code Propagation**: `colab run` and `colab exec` propagate the script's exit status (`sys.exit(0)` → 0, `sys.exit(1)` → 1). Check `$?` for failures.
3. **Guaranteed Teardown with Bash Traps**:
   ```bash
   SESSION="job-$(date +%s)"
   trap "colab stop -s $SESSION || true" EXIT
   colab new -s "$SESSION" --gpu T4
   colab exec -s "$SESSION" -f train.py
   colab download -s "$SESSION" /content/model.pt ./model.pt
   ```

</Agent-Automation-Patterns>

<Connecting-Skills>

- **Prerequisites**: Use `coding-principles` for clean code structure.
- **Companions**: Use `code-as-tools` to author modular tools before dispatching to Colab runtimes, and `create-qa-spectrum` for dataset curation.
- **Successors**: Use `manage-skills` when updating or extending skill definitions.

</Connecting-Skills>

<Anti-Patterns-and-Common-Mistakes>

| Anti-Pattern | Root Cause | Correct Approach |
|---|---|---|
| Relying only on `os.environ` in Colab | Colab secrets are stored in `userdata`, not `os.environ` | Use `userdata.get(...)` and sync to `os.environ` |
| Running `colab auth` to fix local CLI 401/403 | Confusing VM GCP auth with CLI auth | Use `gcloud auth application-default login` with all 4 scopes |
| Missing `-s <name>` on `colab new` | Auto-generates random 6-hex ID | Always name sessions explicitly (e.g. `-s exp01`) |
| Missing self-bootstrapping in Colab notebooks | `ModuleNotFoundError` when opened on Colab | Include the `IN_COLAB` git clone & editable install block in cell 1 |
| Leaving persistent VMs running | Incurring compute quota burn | Use `colab run` (auto-teardown) or bash `trap "colab stop" EXIT` |

</Anti-Patterns-and-Common-Mistakes>

<Examples>

### Interactive Probing & Experimentation Recipe
```bash
# 1. Provision a T4 GPU session
colab new -s probe --gpu T4
# 2. Install dependencies using uv inside VM
colab install -s probe datasets transformers torch litellm
# 3. Upload project modules
colab upload -s probe ./src /content/src
# 4. Probing via REPL or sequential exec
echo "import sys; sys.path.append('/content'); import src" | colab exec -s probe
colab repl -s probe
# 5. Export interactive work to notebook and tear down
colab log -s probe -o exploration_session.ipynb
colab stop -s probe
```

</Examples>

<References>

- [Command Reference](references/command-reference.md): Complete list of flags, subcommands, accelerators, and options.
- [Secrets Guide](references/secrets-and-credentials.md): Managing Colab secrets (`google.colab.userdata`), permissions, and API key syncing.
- [Agent Workflows](references/agent-workflows.md): Unattended pipeline scripts, error recovery, and batch recipes.

</References>
