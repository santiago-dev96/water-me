# AGENTS.md

## Stack

- Python 3.14, Flask 3.1, SQLite3, Bootstrap (static), `black` for formatting
- No `pyproject.toml`, no CI, no tests

## Developer Commands

```bash
# Setup (one-time)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate a session secret key
python scripts/print_secret.py

# Set FLASK_SECRET_KEY in .env (see .env.example)

# Initialize/reset the database (destructive — drops all tables)
flask --app flaskr init-db

# Run dev server
flask --app flaskr run --debug
# Or use the shortcut:
./scripts/start.sh
```

## Architecture

- **App factory**: `flaskr/__init__.py:create_app()` — registers blueprints in order: `db`, `errors`, `auth`, `plants`
- **DB**: `flaskr/db.py` — SQLite with `instance/app_db.sqlite`, schema in `flaskr/schema.sql`
- **Auth**: `flaskr/auth.py` — blueprint at `/auth`, username is email (regex-validated), password requires 12-32 chars with upper/lower/digit/special. Session-based (`session["user_id"]`).
- **Plants**: `flaskr/plants.py` — blueprint at root `/`. One plant per user (hard limit). Image upload at `/add_plant`.
- **Uploads**: stored in `instance/images/` with UUID filenames. Config key is `IMAGES` in `__init__.py` but `plants.py:65` reads `IMAGE_UPLOADS_PATH` — **this is a bug**, uploads will 500.
- **Error handler**: only 500 is handled (`flaskr/errors.py`)

## Conventions

- `.env` loaded via `app.config.from_prefixed_env()` (Flask built-in). Only `FLASK_SECRET_KEY` is used.
- `init-db` is registered as a Flask CLI command in `flaskr/db.py`, not a standalone script.
- `scripts/init_db.sh` and `scripts/start.sh` both activate `.venv` before running flask commands.
- Formats with `black` (no config file, uses defaults).

## Gotchas

- `init-db` drops and recreates all tables — data loss.
- No test suite exists. Any tests added should use `test_config` param in `create_app()`.
- `instance/` directory is gitignored but created at runtime by `create_app()`.
- `plants.py` references `IMAGE_UPLOADS_PATH` config key but `__init__.py` sets `IMAGES` — mismatch causes 500 on upload.
