# Google Colab CLI Command Reference

This document provides a comprehensive reference for the official `google-colab-cli` tool.

---

## 1. Installation & Environment Setup

### Primary Installation (Recommended)
```bash
uv tool install google-colab-cli
```

### Alternative Installation
```bash
pip install google-colab-cli
```

### Verification
```bash
colab version
colab --help
```

> **Note:** Supported on Linux and macOS. Windows requires WSL2.

---

## 2. Authentication (`colab auth`)

| Command | Description |
|---|---|
| `colab auth login` | Initiates browser-based OAuth2 flow to log in |
| `colab auth login --auth=adc` | Authenticates using Application Default Credentials (GCP) |
| `colab auth status` | Displays active credentials, expiration, and connected Google account |
| `colab auth logout` | Clears stored session tokens and OAuth credentials |

---

## 3. Session & Runtime Management

### `colab new`
Provisions a persistent remote runtime. It remains active until explicitly stopped or hitting idle timeouts.

```bash
colab new [OPTIONS]
```

**Options:**
- `-s, --session <NAME>`: Custom name or alias for the session (default: auto-generated ID).
- `--gpu <TYPE>`: Request GPU hardware accelerator. Supported: `T4`, `L4`, `V100`, `A100`, `H100`.
- `--tpu <TYPE>`: Request TPU accelerator. Supported: `v2-8`, `v3-8`, `v5e1`, `v6e1`.
- `--ram <standard|high>`: Select system memory tier (standard ~12GB, high ~50GB).
- `--disk <standard|high>`: Select disk storage tier.

### `colab list`
Lists all active and provisioned sessions with their IDs, runtime types, hardware accelerators, and uptime.
```bash
colab list
```

### `colab stop`
Terminates a session and releases the underlying compute instance to stop billing/quota usage.
```bash
colab stop <SESSION_ID_OR_NAME>
colab stop --all
```

---

## 4. Execution Commands

### `colab run` (Ephemeral / Fire-and-Forget)
Creates an ephemeral instance, runs a script or notebook, streams stdout/stderr locally, and automatically terminates the VM upon completion.

```bash
colab run [OPTIONS] <FILE_OR_COMMAND>
```

**Options:**
- `--gpu <TYPE>`: Hardware accelerator (`T4`, `A100`, etc.).
- `--tpu <TYPE>`: Hardware accelerator.
- `--keep`: Prevents automatic deallocation after execution finishes (keeps VM alive).
- `-s, --session <NAME>`: Name for the ephemeral session.

**Examples:**
```bash
# Run a training script with T4 GPU and auto-terminate
colab run --gpu T4 train.py

# Run a Jupyter notebook
colab run --gpu A100 experiments.ipynb

# Inline one-liner
colab run --gpu T4 "python -c 'import torch; print(torch.cuda.is_available())'"
```

### `colab exec` (Persistent Session Execution)
Executes code or scripts within an already running persistent session. Kernel state (variables, modules) is preserved across multiple calls.

```bash
# Execute local file remotely in session 'my-session'
colab exec -s my-session -f script.py

# Execute arbitrary shell / python command
colab exec -s my-session "pip install -q transformers && python evaluate.py"
```

---

## 5. Interactive Access (`ssh` & `repl`)

| Command | Purpose | Usage |
|---|---|---|
| `colab ssh` | Opens a WebSocket-based interactive shell in `/content` | `colab ssh -s my-session` |
| `colab repl` | Starts an interactive Python REPL connected to the Jupyter kernel | `colab repl -s my-session` |
| `colab console` | Attaches to standard console output stream | `colab console -s my-session` |

---

## 6. File & Storage Operations

The remote root working directory is `/content`.

```bash
# Upload local file/folder to remote runtime
colab upload -s my-session ./local_data /content/data

# Download remote artifacts/checkpoints to local machine
colab download -s my-session /content/checkpoints ./local_checkpoints

# List files in remote directory
colab ls -s my-session /content

# Mount Google Drive into /content/drive
colab drivemount -s my-session
```

---

## 7. Port Forwarding & Web UIs

Tunnel remote web services (e.g. TensorBoard, Gradio, FastAPI) to your local machine:

```bash
# Forward remote port 7860 (Gradio) to local port 7860
colab port-forward -s my-session 7860:7860

# Forward TensorBoard (port 6006)
colab port-forward -s my-session 6006:6006
```

---

## 8. Shebang Script Support

You can add a shebang directly to Python scripts so they execute remotely on Colab when run locally:

```python
#!/usr/bin/env -S colab run --gpu T4
import torch

print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
```
Make executable: `chmod +x script.py && ./script.py`
