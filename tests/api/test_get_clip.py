from __future__ import annotations

from datetime import datetime, timezone


def _parse_rfc3339(dt: str) -> datetime:
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    parsed = datetime.fromisoformat(dt)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def test_get_clip_returns_created_clip(client) -> None:
    # Create contributor first
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Clip Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create a submission that will create a clip
    submission_payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "https://youtu.be/dQw4w9WgXcQ",
        "raw_date_input": "2024-05-12",
        "title": "Test Performance",
        "notes": "Contract test clip",
    }

    create_resp = client.post("/submissions", json=submission_payload)
    assert create_resp.status_code == 201, create_resp.text
    clip_id = create_resp.json()["clip_id"]
    assert clip_id is not None

    # Retrieve the clip
    get_resp = client.get(f"/clips/{clip_id}")
    assert get_resp.status_code == 200, get_resp.text
    data = get_resp.json()

    # Verify all required fields match OpenAPI spec
    assert data["id"] == clip_id
    assert data["youtube_video_id"] == "dQw4w9WgXcQ"
    assert data["youtube_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert data["performance_date"] == "2024-05-12"
    assert data["title"] == "Test Performance"
    assert data["notes"] == "Contract test clip"
    assert data["created_by_contributor_id"] == contributor_id
    assert isinstance(data["added_via_submission_id"], str) and data["added_via_submission_id"]
    assert isinstance(data["created_at"], str) and data["created_at"]
    _parse_rfc3339(data["created_at"])


def test_get_clip_with_null_title_and_notes(client) -> None:
    # Create contributor first
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Null Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create a submission without title or notes
    submission_payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "https://youtu.be/abc123def45",
        "raw_date_input": "2024-06-15",
    }

    create_resp = client.post("/submissions", json=submission_payload)
    assert create_resp.status_code == 201, create_resp.text
    clip_id = create_resp.json()["clip_id"]
    assert clip_id is not None

    # Retrieve the clip
    get_resp = client.get(f"/clips/{clip_id}")
    assert get_resp.status_code == 200, get_resp.text
    data = get_resp.json()

    # Verify null title becomes empty string, notes is null
    assert data["title"] == ""
    assert data["notes"] is None


def test_get_clip_not_found_returns_404(client) -> None:
    resp = client.get("/clips/nonexistent_clip_id")
    assert resp.status_code == 404, resp.text
    assert resp.json()["detail"] == "Not found"

