from __future__ import annotations

from datetime import datetime, timezone


def _parse_rfc3339(dt: str) -> datetime:
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    parsed = datetime.fromisoformat(dt)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def test_create_submission_valid_input_is_accepted_and_returns_clip_id(client) -> None:
    # Create contributor first
    contributor_resp = client.post("/contributors", json={"display_name": "Submission Tester", "external_id": None})
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    submission_payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "https://youtu.be/dQw4w9WgXcQ",
        "raw_date_input": "2024-05-12",
        "title": "Test Performance",
        "notes": "Contract test submission",
    }

    resp = client.post("/submissions", json=submission_payload)

    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data.get("status") == "accepted"
    assert isinstance(data.get("id"), str) and data["id"]
    assert data.get("contributor_id") == contributor_id
    assert isinstance(data.get("submitted_at"), str) and data["submitted_at"]
    _parse_rfc3339(data["submitted_at"])
    assert isinstance(data.get("clip_id"), str) and data["clip_id"]
    assert data.get("raw_youtube_input") == submission_payload["raw_youtube_input"]
    assert data.get("raw_date_input") == submission_payload["raw_date_input"]