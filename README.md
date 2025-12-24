# Time Warp
Time Warp is a human-curated, chronological archive for discovering live music footage without algorithmic feeds.

## Docs
- [PRD](docs/PRD.md)
- [Scope](docs/SCOPE.md)
- [Data Model](docs/DATA_MODEL.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API](docs/API.md)

## Project Context

Time Warp is a new iteration of an earlier personal project exploring chronological discovery of live music footage. This version is being developed from the ground up to reflect current skills, tooling, and architectural judgment, rather than to extend or maintain the original codebase. The goal is to produce a clean, well-documented implementation that demonstrates present-day design and engineering ability.

## Backend (Django)

This project uses **Django + Django REST Framework** as its sole backend. 

### Local Development

From the repository root:

```bash
cd apps/server
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

### Running Tests

From the repository root:

```bash
pytest -q
```

Tests are written as **contract tests** against the HTTP API and should not require any manual server startup.

### Backend Entry Point

- Django project root: `apps/server/`
- Django settings: `config.settings`
- API implementation: `archive/api/`

There is intentionally **one backend** for this repository.