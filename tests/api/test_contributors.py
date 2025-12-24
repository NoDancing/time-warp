from __future__ import annotations

from datetime import datetime, timezone


def _parse_rfc3339(dt: str) -> datetime:
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    parsed = datetime.fromisoformat(dt)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def test_create_contributor_in_process(client) -> None:
    payload = {"display_name": "Test User", "external_id": None}
    resp = client.post("/contributors", json=payload)

    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert isinstance(data.get("id"), str) and data["id"]
    assert isinstance(data.get("created_at"), str) and data["created_at"]
    _parse_rfc3339(data["created_at"])
    assert data.get("display_name") == "Test User"
