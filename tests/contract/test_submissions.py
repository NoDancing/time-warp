from __future__ import annotations

from datetime import datetime, timezone

import requests


def _parse_rfc3339(dt: str) -> datetime:
    # Accept ISO-8601/RFC3339 with optional trailing 'Z'
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    parsed = datetime.fromisoformat(dt)
    # Normalize naive datetimes to UTC for safety (shouldn't happen if API is correct)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def test_create_submission_valid_input_is_accepted_and_returns_clip_id(base_url: str) -> None:
    # Arrange: create a contributor to attribute the submission.
    contributor_payload = {"display_name": "Submission Tester", "external_id": None}
    contributor_resp = requests.post(
        f"{base_url}/contributors", json=contributor_payload, timeout=5
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor = contributor_resp.json()
    contributor_id = contributor["id"]

    # Act: submit a valid YouTube input + performance date.
    submission_payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "https://youtu.be/dQw4w9WgXcQ",
        "raw_date_input": "2024-05-12",
        "title": "Test Performance",
        "notes": "Contract test submission",
    }
    resp = requests.post(f"{base_url}/submissions", json=submission_payload, timeout=5)

    # Assert: contract-level expectations for a successful submission.
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data.get("status") == "accepted"
    assert isinstance(data.get("id"), str) and data["id"]
    assert isinstance(data.get("contributor_id"), str) and data["contributor_id"] == contributor_id

    assert isinstance(data.get("submitted_at"), str) and data["submitted_at"]
    _parse_rfc3339(data["submitted_at"])

    # On acceptance, clip_id must be present.
    assert isinstance(data.get("clip_id"), str) and data["clip_id"]

    # Echo raw inputs (these are part of the audit trail).
    assert data.get("raw_youtube_input") == submission_payload["raw_youtube_input"]
    assert data.get("raw_date_input") == submission_payload["raw_date_input"]
