# Homepage – Agent Context

## Project overview

**homepage** is a full-stack project: **React frontend**, **FastAPI backend**, and a browser **extension**. Root [`package.json`](package.json) orchestrates install, dev, and test for all three (via `concurrently`). Python dependencies for the backend (and tooling) live in root **`pyproject.toml`** / **`uv.lock`**; use **`uv sync`** to install them.

## Repository structure

```
.
├── package.json                   # Root: dev, test, install (backend + frontend + extension)
├── pyproject.toml                 # Python deps, dev groups, pytest config
├── uv.lock
├── backend/
│   ├── __main__.py                # Backend entry
│   └── tests/                     # pytest (see [tool.pytest.ini_options] in pyproject.toml)
├── frontend/                      # React app (package.json)
├── extension/                     # Browser extension
│   ├── package.json
│   └── popup/
│       └── package.json
```

## Tech stack

- **Backend:** Python 3, FastAPI (`backend/__main__.py`), [uv](https://docs.astral.sh/uv/) with root `pyproject.toml`
- **Frontend:** React (see `frontend/package.json`)
- **Extension:** Node (see `extension/package.json`, `extension/popup/package.json`)
- **Root:** Node with `concurrently` — see scripts in root `package.json`

## Setup

From repo root:

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if it is not already available.
2. Install root dev dependency and all packages (Python via uv, frontend and extension via npm):
   ```bash
   npm install
   npm run install
   ```
   `npm run install` runs `install:backend` (`uv sync`), `install:frontend`, and `install:extension` in parallel per root `package.json`.

Python only:

```bash
uv sync
```

## Running / entry points

| Goal | Command |
|------|---------|
| Full stack | `npm run dev` — `dev:backend` (`cd backend && uv run python __main__.py`) + `dev:frontend` |
| Frontend only | `npm run dev:frontend` or `cd frontend && npm run dev` |
| Backend only | `cd backend && uv run python __main__.py` (after `uv sync`) |
| Extension | Load unpacked from `extension/` (and popup if built separately) in the browser |

## Tests

| Scope | Command |
|-------|---------|
| All | `npm run test` — backend (`uv run pytest`), frontend, extension |
| Backend | `npm run test:backend` or `uv run pytest` (from repo root; options in `pyproject.toml`) |
| Frontend | `npm run test:frontend` or `cd frontend && npm test` |
| Extension | `npm run test:extension` / `npm run test:extension:main` |

## Code conventions

- Backend: Python/FastAPI; tests in `backend/tests/` run with **pytest** (configured in root `pyproject.toml`).
- Frontend/extension: per their `package.json` and README.

## Important files

| Path | Purpose |
|------|--------|
| `package.json` | Root scripts (`dev`, `test`, `install`, and `:*` variants) |
| `pyproject.toml` | Python project metadata, dependency groups, `[tool.pytest.ini_options]` |
| `uv.lock` | Locked Python dependency versions |
| `backend/__main__.py` | FastAPI entry |
| `frontend/package.json` | Frontend app |
| `extension/package.json` | Extension build |

## Sensitive / ignored files

Do not commit or suggest adding:

- **Env:** `.env`, API keys
- **Python env:** `.venv/` (repo root), `backend/.venv/`, `backend/venv/`
- **Node:** `node_modules/`
- **Build:** `dist/`, build artifacts
