from __future__ import annotations

from datetime import datetime, timezone


def _parse_rfc3339(dt: str) -> datetime:
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    parsed = datetime.fromisoformat(dt)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def test_create_submission_invalid_date_is_rejected_and_has_no_clip_id(client) -> None:
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "https://youtu.be/dQw4w9WgXcQ",
        "raw_date_input": "2024-99-99",
        "title": "Bad Date",
        "notes": "Should reject",
    }

    resp = client.post("/submissions", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data["status"] == "rejected"
    assert isinstance(data.get("id"), str) and data["id"]
    assert data["contributor_id"] == contributor_id
    assert isinstance(data.get("submitted_at"), str) and data["submitted_at"]
    _parse_rfc3339(data["submitted_at"])

    assert data.get("clip_id") is None
    assert isinstance(data.get("validation_error"), str) and data["validation_error"]

    # still echoes inputs
    assert data["raw_youtube_input"] == payload["raw_youtube_input"]
    assert data["raw_date_input"] == payload["raw_date_input"]
