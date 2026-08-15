# Google Colab CLI Command Reference

This document provides a comprehensive reference for all commands and options in `google-colab-cli`.

---

## 1. Global Options

Global options must precede the subcommand: `colab [GLOBAL_OPTIONS] COMMAND [ARGS...]`

| Option | Flag | Description | Default |
|---|---|---|---|
| `--auth` | | Authentication strategy: `adc` or `oauth2` | `adc` |
| `--client-oauth-config` | `-c` | Path to client OAuth config JSON | `~/.colab-cli-oauth-config.json` |
| `--config` | | Path to session state file | `~/.config/colab-cli/sessions.json` |
| `--logtostderr` | | Log all output to stderr | `False` |

---

## 2. Session Management Commands

### `colab new`
Allocates a new CPU, GPU, or TPU VM runtime.
```bash
colab new [OPTIONS]
```
- `-s, --session <NAME>`: Custom name for the session (recommended to avoid auto-generated hex IDs).
- `--gpu <TYPE>`: Request GPU accelerator (`T4`, `L4`, `G4`, `A100`, `H100`).
- `--tpu <TYPE>`: Request TPU accelerator (`v5e1`, `v6e1`).
- *Note:* If both `--gpu` and `--tpu` are omitted, a standard CPU runtime is provisioned.

### `colab sessions`
Lists all active sessions on the backend and synchronizes local metadata.
```bash
colab sessions
```

### `colab status`
Displays hardware accelerator, IDLE/BUSY state, and last executed command.
```bash
colab status [-s NAME]
```

### `colab restart-kernel`
Restarts the active session's Jupyter kernel without releasing the VM instance.
```bash
colab restart-kernel [-s NAME]
```

### `colab stop`
Terminates the remote VM and shuts down its keep-alive background daemon.
```bash
colab stop [-s NAME]
```

### `colab url`
Prints or opens a browser URL that attaches the Colab web UI directly to the existing CLI VM and kernel.
```bash
colab url [-s NAME] [--open] [--host <ORIGIN>]
```
- `--open`: Opens the attachment URL directly in the default web browser.

---

## 3. Code Execution Commands

### `colab run` (Ephemeral Runner)
Allocates a fresh VM, runs a script or notebook with arguments, and tears down the VM upon completion.
```bash
colab run [OPTIONS] SCRIPT_PATH [ARGS...]
```
- `--gpu <TYPE>`: Hardware accelerator.
- `--tpu <TYPE>`: Hardware accelerator.
- `--keep`: Preserves the VM on completion instead of terminating it.
- `-s, --session <NAME>`: Optional session name.

### `colab exec` (Persistent Kernel Execution)
Executes Python code or a notebook inside an active session. Kernel variables and loaded modules persist across calls.
```bash
colab exec [OPTIONS]
```
- `-s, --session <NAME>`: Target session name.
- `-f, --file <PATH>`: Local `.py` or `.ipynb` file to execute remotely (read locally and streamed).
- `--timeout <FLOAT>`: Execution timeout in seconds (default: `30.0`).
- `--output-image <PATH>`: Save intercepted plot/figure outputs directly to a local image file.

### `colab repl` (Interactive Python REPL)
Starts an interactive Python REPL directly connected to the remote Jupyter kernel.
```bash
colab repl [-s NAME] [--output-image PATH]
```

### `colab console` (Raw Terminal Shell)
Connects to an interactive tmux/bash session in `/content` on the remote VM.
```bash
colab console [-s NAME]
```

---

## 4. File & Package Operations

All remote paths default to `/content`.

### `colab install`
Installs packages inside the VM using `uv pip install --system` (falls back to `pip`).
```bash
colab install [-s NAME] [PACKAGES...] [-r REQUIREMENTS_FILE]
```

### `colab upload`
Uploads a local file or directory to the remote VM.
```bash
colab upload [-s NAME] LOCAL_PATH REMOTE_PATH
```

### `colab download`
Downloads a file or directory from the remote VM to the local system.
```bash
colab download [-s NAME] REMOTE_PATH LOCAL_PATH
```

### `colab edit`
Opens a remote file in your local `$EDITOR` for in-place modification.
```bash
colab edit [-s NAME] REMOTE_PATH
```

### `colab ls` / `colab rm`
Lists or deletes files on the remote VM.
```bash
colab ls [-s NAME] [REMOTE_PATH]
colab rm [-s NAME] REMOTE_PATH
```

### `colab drivemount`
Mounts Google Drive at `/content/drive` (interactive).
```bash
colab drivemount [-s NAME] [PATH]
```

---

## 5. History & Exporting (`colab log`)

Views or exports the session execution history:
```bash
colab log [-s NAME] [-n LINES] [-t EVENT_TYPE] [-o OUTPUT_PATH]
```
The file format is automatically selected based on the extension of `-o`:
- `.ipynb` — Jupyter Notebook
- `.md` — Markdown summary report
- `.jsonl` — Raw structured JSON logs
- `.txt` — Plain text log
