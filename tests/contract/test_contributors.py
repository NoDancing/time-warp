from __future__ import annotations

from datetime import datetime, timezone

import requests


def _parse_rfc3339(dt: str) -> datetime:
    # Accepts ISO-8601/RFC3339 with optional trailing 'Z'
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    parsed = datetime.fromisoformat(dt)
    # Normalize naive datetimes to UTC for safety (shouldn't happen if API is correct)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def test_create_contributor_returns_201_and_minimal_contract(base_url: str) -> None:
    payload = {
        "display_name": "Test User",
        "external_id": None,
    }

    resp = requests.post(f"{base_url}/contributors", json=payload, timeout=5)

    assert resp.status_code == 201, resp.text
    data = resp.json()

    # Contract-minimum fields
    assert isinstance(data.get("id"), str) and data["id"], "Contributor.id must be a non-empty string"
    assert isinstance(data.get("created_at"), str) and data["created_at"], "Contributor.created_at must be present"

    # RFC3339 / ISO-8601 datetime parseable
    _parse_rfc3339(data["created_at"])

    # Echo behavior (safe expectation; if you later choose not to echo, change this assertion)
    assert data.get("display_name") == "Test User"