# Architecture

## Overview

A CLI tool + static site that bridges Raindrop.io bookmarks to a GitHub Pages random redirect.

```
Raindrop.io API ──→ CLI (fetch/sync) ──→ urls.txt ──→ GitHub Pages (index.html)
                                              ↓
                                         git commit+push
```

## Components

### CLI (`src/unread_articles/cli.py`)
- Typer-based CLI with two commands: `fetch` and `sync`
- Loads `.env` via `python-dotenv` for the API token
- Resolves `urls.txt` path relative to git root
- Entry point: `unread-articles = "unread_articles.cli:app"` (defined in `pyproject.toml`)

### Raindrop Client (`src/unread_articles/raindrop.py`)
- `build_search_query()` — converts tag list to Raindrop's `#"tag"` syntax
- `fetch_all_urls()` — paginates through Raindrop API, extracts `link` from each item
- `save_urls()` — writes URL list to file (one per line, overwrites)
- Uses `httpx` for HTTP with 30s timeout

### Git Operations (`src/unread_articles/git_ops.py`)
- `commit_and_push()` — stages specific files, commits, pushes
- Default commit message: `"updated urls - YYYY-MM-DD"` (UTC)
- Uses `subprocess.run` with `check=True`

### GitHub Pages (`index.html`)
- Fetches `urls.txt` via relative `fetch()`
- Picks random URL, redirects with `window.location.href`
- Dark-themed loading spinner (visible briefly before redirect)
- Handles empty list and fetch errors gracefully

## Data Flow

1. User runs `unread-articles fetch <tags>`
2. CLI calls Raindrop API with tag search query
3. API returns paginated bookmark items
4. URLs extracted and written to `urls.txt`
5. (If `sync`) Git stages `urls.txt`, commits, pushes
6. GitHub Pages serves `index.html` which reads `urls.txt` and redirects

## Key Decisions

- **`urls.txt` is committed** — it must be served by GitHub Pages, so it's tracked in git
- **Collection ID defaults to 0** — Raindrop's "all collections" alias
- **AND logic for tags** — multiple tags narrow results (Raindrop's default behavior)
- **Overwrite, not append** — `fetch` always overwrites `urls.txt` for a clean state

## Testing

- Tests in `tests/test_raindrop.py` using `pytest-httpx` for mocking HTTP
- Covers: query building, URL saving, pagination, auth headers, error handling
- Run: `uv run pytest -v`
