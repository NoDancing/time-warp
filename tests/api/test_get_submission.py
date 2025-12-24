from __future__ import annotations

from datetime import datetime, timezone


def _parse_rfc3339(dt: str) -> datetime:
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    parsed = datetime.fromisoformat(dt)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def test_get_submission_returns_created_submission(client) -> None:
    # Create contributor first
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Get Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create a submission
    submission_payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "https://youtu.be/dQw4w9WgXcQ",
        "raw_date_input": "2024-05-12",
        "title": "Test Performance",
        "notes": "Contract test submission",
    }

    create_resp = client.post("/submissions", json=submission_payload)
    assert create_resp.status_code == 201, create_resp.text
    submission_id = create_resp.json()["id"]

    # Retrieve the submission
    get_resp = client.get(f"/submissions/{submission_id}")
    assert get_resp.status_code == 200, get_resp.text
    data = get_resp.json()

    # Verify all fields match
    assert data["id"] == submission_id
    assert data["contributor_id"] == contributor_id
    assert data["status"] == "accepted"
    assert data["raw_youtube_input"] == submission_payload["raw_youtube_input"]
    assert data["raw_date_input"] == submission_payload["raw_date_input"]
    assert data["title"] == submission_payload["title"]
    assert data["notes"] == submission_payload["notes"]
    assert isinstance(data["clip_id"], str) and data["clip_id"]
    assert data.get("validation_error") is None
    assert isinstance(data["submitted_at"], str) and data["submitted_at"]
    _parse_rfc3339(data["submitted_at"])


def test_get_submission_rejected_has_no_clip_id(client) -> None:
    # Create contributor first
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Rejected Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create a rejected submission (invalid YouTube URL)
    submission_payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "not a url",
        "raw_date_input": "2024-05-12",
        "title": "Bad Submission",
        "notes": "Should be rejected",
    }

    create_resp = client.post("/submissions", json=submission_payload)
    assert create_resp.status_code == 201, create_resp.text
    submission_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "rejected"

    # Retrieve the submission
    get_resp = client.get(f"/submissions/{submission_id}")
    assert get_resp.status_code == 200, get_resp.text
    data = get_resp.json()

    # Verify rejected submission fields
    assert data["id"] == submission_id
    assert data["contributor_id"] == contributor_id
    assert data["status"] == "rejected"
    assert data["clip_id"] is None
    assert isinstance(data["validation_error"], str) and data["validation_error"]
    assert data["raw_youtube_input"] == submission_payload["raw_youtube_input"]
    assert data["raw_date_input"] == submission_payload["raw_date_input"]


def test_get_submission_not_found_returns_404(client) -> None:
    resp = client.get("/submissions/nonexistent_id")
    assert resp.status_code == 404, resp.text
