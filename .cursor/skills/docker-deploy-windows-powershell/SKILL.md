---
name: docker-deploy-windows-powershell
description: Deploys the homepage stack locally via Docker using the deployment CLI on native Windows PowerShell with a Windows uv environment (not WSL or Linux). Use when the user asks for Docker deploy, deploy.py, docker-deploy-strategy, or running deployment on Windows outside WSL.
---

# Homepage Docker deploy (Windows PowerShell, native uv)

## Scope

- **Host:** Windows, **Windows PowerShell** (desktop session).
- **Python / uv:** **Native Windows** install only. Do **not** use WSL, Git Bash on Linux paths, or a `.venv` created under WSL for this workflow.
- **Goal:** Run the `docker-deploy-strategy` deployment strategy so Docker Compose brings the app up locally.

## Why avoid WSL here

- The project path, `.venv`, and `uv` must align with **Windows** Python so subprocesses and Docker Desktop integration match how the strategy invokes `docker` / `docker compose`.
- Mixing WSL `uv` with a repo checked out on `/mnt/c/...` or duplicating venvs causes confusing failures; keep one canonical environment on Windows for this deploy path.

## Prerequisites

1. **Docker Desktop for Windows** installed and running (Linux containers mode is typical).
2. **`uv` for Windows** on `PATH` (install from [Astral uv docs](https://docs.astral.sh/uv/getting-started/installation/) if needed).
3. Repo root on a **Windows** path (e.g. `C:\Users\...\homepage`), not only accessed from WSL.

## One-time setup (from repo root)

In **PowerShell**, `cd` to the homepage project root (the directory that contains `deploy.py` and `pyproject.toml`).

Sync Python deps (includes the `dev` group, which provides `fire` for `deploy.py`):

```powershell
uv sync
```

If `uv run` cannot import `fire`, run an explicit dev sync:

```powershell
uv sync --group dev
```

## Deploy (install strategy)

From the **same** repo root, in **Windows PowerShell**:

```powershell
uv run python .\deploy.py strategy install docker-deploy-strategy
```

`./deploy.py` is also valid in PowerShell; prefer `.\deploy.py` if you hit path quirks.

## Useful CLI commands

- List strategies (confirm name is `docker-deploy-strategy`):

```powershell
uv run python .\deploy.py strategy list
```

- Tear down the strategy:

```powershell
uv run python .\deploy.py strategy uninstall docker-deploy-strategy
```

- High-level CLI help pattern matches `deployment/src/cli.py` (subcommands `step` and `strategy`).

## Agent checklist

- [ ] Instruct **Windows PowerShell** and **Windows `uv`**, explicitly **not WSL**.
- [ ] Working directory = homepage root (`deploy.py` visible).
- [ ] `uv sync` (or `--group dev`) mentioned if `deploy.py` fails on missing `fire`.
- [ ] Docker Desktop running before `strategy install`.
- [ ] Strategy id is **`docker-deploy-strategy`** (kebab-case from `DockerDeployStrategy`), not `docker-deploy` unless the user’s CLI/registry differs—verify with `strategy list` if unsure.
