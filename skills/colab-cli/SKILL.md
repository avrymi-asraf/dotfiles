---
name: colab-cli
description: Provision Google Colab cloud runtimes, execute remote Python scripts and notebooks, manage files, open SSH sessions, and run compute tasks directly from the terminal via the official Google Colab CLI. Use when running code on Google Colab GPUs/TPUs, provisioning remote environments, streaming outputs, or using colab-cli in agentic workflows.
---

<colab-cli>

Google Colab CLI (`google-colab-cli`) connects local terminals and autonomous agents directly to Google Colab cloud runtimes. It enables allocating CPU, GPU (T4, L4, G4, A100, H100), or TPU (v5e1, v6e1) instances, exploring data interactively, executing Python scripts/notebooks remotely with real-time output streaming, transferring files, and managing VM lifecycles without opening a browser.

### Topics Covered
- **Use [Installation-and-Auth]** for installing `google-colab-cli` and configuring ADC / OAuth2 scopes.
- **Use [Runtime-Management]** for provisioning (`new`), listing (`sessions`), inspecting (`status`), and stopping sessions.
- **Use [Interactive-Exploration]** for interactive data probing via REPL, console shell, and Colab web UI attachment (`url`).
- **Use [Execution-Modes]** for ephemeral jobs (`run`), persistent kernel execution (`exec`), and shebang scripts.
- **Use [File-and-Package-Management]** for transferring datasets, editing remote files (`edit`), and installing packages (`install`).
- **Use [Colab-Notebook-Bootstrapping]** for self-cloning and setting up repository dependencies when notebooks run in Colab kernel environments.
- **Use [Agent-Automation-Patterns]** for headless scripts, stdout/stderr streams, error codes, and session isolation.
- **Use [Anti-Patterns-and-Common-Mistakes]** to avoid auth traps, scope errors, and idle resource costs.
- **Use [Examples]** for practical, end-to-end interactive and batch recipes.
- Reference [Command Reference](references/command-reference.md) and [Agent Workflows](references/agent-workflows.md) for full flag details.

</colab-cli>

<Installation-and-Auth>

### Package Installation
Install the official Google Colab CLI tool:
```bash
# Recommended installation via uv
uv tool install google-colab-cli

# Alternative via pip
pip install google-colab-cli
```

### Authentication Strategies
The CLI supports two authentication modes via the global flag `--auth={adc,oauth2}` (default is `adc`).

1. **Application Default Credentials (ADC) — Recommended for Headless & Agents**:
   The Colab backend requires four specific scopes. Log in once with `gcloud`:
   ```bash
   gcloud auth application-default login \
     --scopes=openid,\
   https://www.googleapis.com/auth/cloud-platform,\
   https://www.googleapis.com/auth/userinfo.email,\
   https://www.googleapis.com/auth/colaboratory
   ```
   - `userinfo.email`: Required for session backend (`colab.research.google.com`).
   - `colaboratory`: Required for keep-alive RPCs (`colab.pa.googleapis.com`).
   - `openid` + `cloud-platform`: Required by `gcloud`.

2. **OAuth2 Flow**:
   Triggers browser consent on first use:
   ```bash
   colab --auth=oauth2 sessions
   ```

3. **Verify Auth**:
   - `colab sessions`: Read-only check for server connectivity.
   - `colab whoami`: Debug command displaying active email, audience, scopes, and token expiration.

> [!NOTE]
> `colab auth` is for injecting *VM-side* GCP credentials into the running kernel for BigQuery/GCS. It is **not** used to authenticate the local CLI itself.

</Installation-and-Auth>

<Runtime-Management>

### 1. Persistent Session Management (`colab new` / `colab stop`)
Maintains runtime state and kernel memory across multiple commands:
```bash
# Provision named session (always specify -s to avoid random IDs)
colab new -s explore --gpu T4

# Provision with TPU and high RAM
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

Supported accelerators:
- `--gpu`: `T4`, `L4`, `G4`, `A100`, `H100` (defaults to CPU if omitted).
- `--tpu`: `v5e1`, `v6e1`.

### 2. Ephemeral Job Runner (`colab run`)
Provisions a fresh VM, runs the script/notebook, streams output, and automatically terminates the VM:
```bash
# Run script with GPU accelerator and auto-terminate
colab run --gpu T4 train.py
```

</Runtime-Management>

<Interactive-Exploration>

Colab CLI provides four complementary ways to interactively probe data, debug models, and test code:

### 1. Interactive Python REPL (`colab repl`)
Drops directly into a live Python shell on the remote Colab VM. All variables, imports, and loaded datasets remain in kernel memory between commands:
```bash
colab repl -s explore
# Intercept generated plots/images to a local path:
colab repl -s explore --output-image ./latest_plot.png
```

### 2. Full Remote Shell Console (`colab console`)
Connects to an interactive tmux/bash session in `/content` on the remote instance:
```bash
colab console -s explore
# Inside console: run ipython, check nvidia-smi, or inspect files
```

### 3. Attach Colab Web Notebook to CLI VM (`colab url`)
Connects the Google Colab web UI directly to the existing CLI-created VM and kernel, without allocating duplicate resources:
```bash
# Print attachment URL or open directly in browser
colab url -s explore --open
```

### 4. Step-by-Step Code Probing (`colab exec`)
Because `colab exec` targets the persistent kernel, state accumulates across calls:
```bash
# Step 1: Load data once into memory
echo "import pandas as pd; df = pd.read_csv('/content/data.csv')" | colab exec -s explore

# Step 2: Query or probe the loaded DataFrame
echo "print(df.describe())" | colab exec -s explore

# Step 3: Export the entire interactive history to a notebook or markdown report
colab log -s explore -o exploration_report.ipynb
```

</Interactive-Exploration>

<Execution-Modes>

| Mode | Command | Behavior |
|---|---|---|
| **Ephemeral Run** | `colab run --gpu T4 script.py [args]` | Full lifecycle: new VM → execute → teardown |
| **Session Exec** | `colab exec -s <name> -f script.py` | Transmits local file to remote kernel; keeps state |
| **Piped Exec** | `echo "print(1)" \| colab exec -s <name>` | Executes piped code on remote kernel |
| **Notebook Exec** | `colab exec -s <name> -f notebook.ipynb` | Runs cells, writes output to `notebook_output.ipynb` |
| **Shell Console** | `colab console -s <name>` | Raw interactive TTY / tmux shell on remote VM |
| **Interactive REPL** | `colab repl -s <name>` | Python REPL on remote kernel (requires TTY or piped EOF) |

### Shebang Execution Support
Add a shebang to make Python scripts automatically run on cloud hardware:
```python
#!/usr/bin/env -S colab run --gpu T4
import torch
print("CUDA Device:", torch.cuda.get_device_name(0))
```
Make executable with `chmod +x script.py` and run `./script.py`.

</Execution-Modes>

<File-and-Package-Management>

The remote working directory is always `/content`.

```bash
# Install packages in the remote VM using high-performance uv
colab install -s explore torch transformers datasets
colab install -s explore -r requirements.txt

# Upload local files or directories
colab upload -s explore ./local_dir /content/remote_dir

# Download remote artifacts or checkpoints
colab download -s explore /content/checkpoint.pt ./checkpoints/

# Edit remote files in-place using local $EDITOR
colab edit -s explore /content/remote_dir/config.json

# List and delete remote files
colab ls -s explore /content
colab rm -s explore /content/temp_data.csv

# Mount Google Drive to /content/drive (interactive)
colab drivemount -s explore
```

</File-and-Package-Management>

<Colab-Notebook-Bootstrapping>

### Self-Cloning & Setup for Notebooks Running in Colab Kernel

When a notebook is opened directly in Google Colab (e.g., from a GitHub badge or uploaded without local workspace files), the remote VM `/content` environment does not contain the repository code or package files.

To make notebooks immediately executable without manual user cloning, always include this self-bootstrapping pattern in the initial setup cell:

```python
import os
import sys

# 1. Detect Google Colab environment vs local workspace
IN_COLAB = "google.colab" in sys.modules or os.path.exists("/content")

if IN_COLAB:
    print("🚀 Running on Google Colab. Setting up repository and environment...")
    REPO_DIR = "/content/<repo-name>"
    if not os.path.exists(REPO_DIR):
        !git clone https://github.com/<owner>/<repo-name>.git {REPO_DIR}
    %cd {REPO_DIR}
    !pip install -q -e .
    if REPO_DIR not in sys.path:
        sys.path.insert(0, REPO_DIR)
    print("✅ Repository cloned and package installed in editable mode!")
else:
    print("💻 Running in local workspace.")

# 2. Import package modules
import your_package as pkg
```

**Key Advantages:**
1. **Zero-Configuration Colab Execution:** Users opening the notebook in Google Colab can run all cells sequentially without manual terminal cloning or environment setup.
2. **Editable Installation (`pip install -q -e .`):** Automatically installs dependencies from `pyproject.toml` or `setup.py` and supports immediate edits to source files.
3. **Local Safety:** Evaluates `IN_COLAB` as `False` in local Jupyter or VS Code kernels, avoiding unnecessary cloning or directory switching.

</Colab-Notebook-Bootstrapping>

<Agent-Automation-Patterns>

1. **Stream Separation**:
   `colab run` writes CLI status logs to **stderr** and script output to **stdout**. Capturing stdout yields clean program output:
   ```bash
   colab run --gpu T4 eval.py > output.json 2> run.log
   ```

2. **Exit Code Propagation**:
   `colab run` and `colab exec` propagate the script's exit status (`sys.exit(0)` → 0, `sys.exit(1)` → 1). Check `$?` to detect remote script errors.

3. **Guaranteed Resource Teardown with Bash Traps**:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   SESSION="job-$(date +%s)"
   trap "colab stop -s $SESSION || true" EXIT

   colab new -s "$SESSION" --gpu T4
   colab install -s "$SESSION" torch transformers
   colab exec -s "$SESSION" -f run_train.py
   colab download -s "$SESSION" /content/model.pt ./model.pt
   ```

4. **Isolating Concurrent Agent Runs**:
   Use `--config` to prevent concurrent agents from colliding on `~/.config/colab-cli/sessions.json`:
   ```bash
   colab --config /tmp/agent_session.json new -s agent-job --gpu T4
   ```

</Agent-Automation-Patterns>

<Connecting-Skills>

- **Prerequisites**: Use `coding-principles` for clean code structure.
- **Companions**: Use `code-as-tools` to build modular, notebook-compatible experimentation tools before dispatching them to remote Colab runtimes.
- **Successors**: Use `manage-skills` when updating or extending skill definitions.

</Connecting-Skills>

<Anti-Patterns-and-Common-Mistakes>

| Anti-Pattern | Root Cause | Correct Approach |
|---|---|---|
| Running `colab auth` to fix local CLI 401/403 | Confusing VM GCP auth with CLI auth | Use `gcloud auth application-default login` with all 4 scopes |
| Missing `-s <name>` on `colab new` | Auto-generates random 6-hex ID | Always name sessions explicitly (e.g. `-s exp01`) |
| Manually uploading scripts before `colab exec` | Unnecessary overhead | `colab exec -f script.py` automatically reads and transmits locally |
| Missing self-bootstrapping in Colab notebooks | `ModuleNotFoundError` when opened on Colab | Include the `IN_COLAB` git clone & editable install block in cell 1 |
| Leaving persistent VMs running | Incurring compute quota burn | Use `colab run` (auto-teardown) or bash `trap "colab stop" EXIT` |
| Calling interactive commands in headless scripts | Hanging non-interactive shells | Pipe EOF for `repl`/`console`; avoid interactive `drivemount` |

</Anti-Patterns-and-Common-Mistakes>

<Examples>

### Interactive Probing & Experimentation Recipe
```bash
# 1. Provision a T4 GPU session
colab new -s probe --gpu T4

# 2. Install dependencies using uv inside VM
colab install -s probe datasets transformers torch

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
- [Agent Workflows](references/agent-workflows.md): Unattended pipeline scripts, error recovery, and batch recipes.

</References>
