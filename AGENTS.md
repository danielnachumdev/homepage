# Homepage – Agent Context

## Project overview

**homepage** is a full-stack project: **React frontend**, **FastAPI backend**, and a browser **extension**. Root `package.json` orchestrates install, dev, and test for all three. Monorepo-style; backend has its own venv and requirements.

## Repository structure

```
.
├── package.json                   # Root: dev, test, install (backend + frontend + extension)
├── backend/
│   ├── __main__.py                # Backend entry
│   ├── requirements.txt
│   ├── venv/                      # Python venv (create locally)
│   └── tests/                     # unittest (test_*.py)
├── frontend/                      # React app (package.json)
├── extension/                     # Browser extension
│   ├── package.json
│   └── popup/
│       └── package.json
```

## Tech stack

- **Backend:** Python 3, FastAPI (`backend/__main__.py`, `requirements.txt`)
- **Frontend:** React (see `frontend/package.json`)
- **Extension:** Node (see `extension/package.json`, `extension/popup/package.json`)
- **Root:** Node with concurrently for running multiple processes

## Setup

From repo root:

1. Backend: create venv and install:
   ```bash
   cd backend && python -m venv venv
   # Windows: .\backend\venv\Scripts\activate
   # Linux/macOS: source backend/venv/bin/activate
   pip install -r requirements.txt
   ```
2. Frontend and extension:
   ```bash
   npm run install
   ```
   (Runs install for frontend and extension per package.json.)

## Running / entry points

- **Full stack:** `npm run dev` (runs backend + frontend concurrently).
  - Backend: `.\backend\venv\Scripts\python.exe .\backend\__main__.py` (Windows) or equivalent with venv python.
  - Frontend: `cd frontend && npm run dev`.
- **Backend only:** From repo root with venv: `python backend/__main__.py` (or use path to venv python).
- **Frontend only:** `cd frontend && npm run dev`.
- **Extension:** Load unpacked from `extension/` (and popup if built separately) in browser.

## Tests

- **All:** `npm run test` (backend + frontend + extension).
- **Backend:** `cd backend && venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"` (Windows); use `python` from venv on Linux/macOS.
- **Frontend:** `cd frontend && npm test`.
- **Extension:** `npm run test:extension` / `test:extension:main` (extension folder).

## Code conventions

- Backend: Python/FastAPI; unittest in `tests/`.
- Frontend/extension: per their package.json and README.

## Important files

| Path | Purpose |
|------|--------|
| `package.json` | Root scripts (dev, test, install) |
| `backend/__main__.py` | FastAPI entry |
| `backend/requirements.txt` | Python deps |
| `frontend/package.json` | Frontend app |
| `extension/package.json` | Extension build |

## Sensitive / ignored files

Do not commit or suggest adding:

- **Env:** `.env`, API keys
- **Venv:** `backend/venv/`
- **Node:** `node_modules/`
- **Build:** `dist/`, build artifacts
