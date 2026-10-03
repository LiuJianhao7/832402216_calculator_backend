# 832402216 Calculator Backend

Backend project: Software Engineering Practice Assignment 1 — a frontend/backend separated calculator.

- Student: 刘鉴浩 (Liu Jianhao)
- Student ID: 832402216
- Tech stack: Python 3.10+ / WSGI / SQLite / unittest
- Runtime dependencies: **Python standard library only, no third-party runtime dependencies**
- Core principle: the browser does not compute the final result; expression parsing, error handling, and history persistence are all done on the backend.

## Features

- Basic arithmetic: `+ - * /`
- Compound expressions and operator precedence
- Parentheses
- Decimals
- Unary plus/minus (e.g. `-5 + 8`, `3 * -2`)
- Invalid expression detection
- Division by zero detection
- SQLite-persisted calculation history
- Query, search, delete a single entry, clear history
- Statistics for the total history count
- CORS support
- Does not use `eval` / `exec`

## Project Structure

```text
832402216_calculator_backend/
├── src/
│   ├── app.py          # WSGI HTTP/JSON API
│   ├── database.py     # SQLite data access
│   ├── parser.py       # Safe recursive descent expression parser
│   └── run.py          # Local development entry point
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_parser.py
├── requirements.txt
├── README.md
└── codestyle.md
```

## Local Startup

No need to install Flask or any other third-party packages:

```bash
cd 832402216_calculator_backend
python src/run.py
```

Default address: `http://127.0.0.1:5000`

Health check: `GET http://127.0.0.1:5000/health`

The SQLite file is automatically created by default at `data/calculator.db`.

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/calculate` | Parse and calculate the expression on the backend, and save it to history on success |
| `GET` | `/api/history` | Query history records; supports `?search=keyword` |
| `DELETE` | `/api/history/<id>` | Delete a specific history entry |
| `DELETE` | `/api/history` | Clear all history (extended feature) |
| `GET` | `/api/stats` | Query the history count (extended feature) |

Example calculation request:

```json
{
  "expression": "(1+2)*3"
}
```

Example successful response:

```json
{
  "success": true,
  "expression": "(1+2)*3",
  "result": "9",
  "history": {
    "id": 1,
    "expression": "(1+2)*3",
    "result": "9",
    "created_at": "2026-10-01T12:00:00+00:00"
  }
}
```

## Environment Variables

| Name | Default | Meaning |
|---|---|---|
| `CALCULATOR_DB_PATH` | `data/calculator.db` | Location of the SQLite database file |
| `ALLOWED_ORIGINS` | `*` | Frontend origins allowed by CORS; separate multiple origins with commas |

For production deployment, it is recommended to change `ALLOWED_ORIGINS` to your GitHub Pages URL.

## Automated Tests

```bash
python -m unittest discover -s tests -v
```

Tests cover core expressions, precedence, parentheses, decimals, unary plus/minus, division by zero, invalid input, the real HTTP API, and history write/delete.

## PythonAnywhere Deployment

1. Create an account on PythonAnywhere and open a Bash Console.
2. Run:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/832402216_calculator_backend.git
```

3. Open **Web** → **Add a new web app** → select **Manual configuration** → Python 3.x.
4. Open the Web App's **WSGI configuration file** and change the project part to:

```python
import os
import sys

project_src = '/home/YOUR_PYTHONANYWHERE_USERNAME/832402216_calculator_backend/src'
if project_src not in sys.path:
    sys.path.insert(0, project_src)

# Optional: replace * with your GitHub Pages domain after going live
os.environ['ALLOWED_ORIGINS'] = '*'

from app import application
```

5. Click **Reload**.
6. Open:

```text
https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com/health
```

If you see `success: true`, the deployment succeeded.
7. Change the production API URL in the frontend `src/config.js` to that domain.

> SQLite resides in the persistent file system of the PythonAnywhere user directory, so history is still retained after page refreshes, browser restarts, and Web App Reloads.

## Frontend/Backend Connection

For local development, the frontend `config.js` automatically uses `http://127.0.0.1:5000`.
For production deployment, replace `https://YOUR_USERNAME.pythonanywhere.com` in `config.js` with the real backend domain, then push the frontend repository and enable GitHub Pages.
