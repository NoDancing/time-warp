from __future__ import annotations


def test_create_submission_duplicate_clip_returns_409_and_rejected_submission(
    client,
) -> None:
    """Two accepted submissions with the same (youtube_video_id, performance_date) should return 409 Conflict on the second attempt."""
    # Create contributor first
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Duplicate Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    submission_payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "https://youtu.be/dQw4w9WgXcQ",
        "raw_date_input": "2024-05-12",
        "title": "First Performance",
        "notes": "First submission",
    }

    # First submission should succeed
    first_resp = client.post("/submissions", json=submission_payload)
    assert first_resp.status_code == 201, first_resp.text
    first_data = first_resp.json()
    assert first_data.get("status") == "accepted"
    assert first_data.get("clip_id") is not None

    # Second submission with same (youtube_video_id, performance_date) should return 409
    second_resp = client.post("/submissions", json=submission_payload)
    assert second_resp.status_code == 409, second_resp.text
    second_data = second_resp.json()

    # Still creates a Submission record with rejected status
    assert second_data.get("status") == "rejected"
    assert isinstance(second_data.get("id"), str) and second_data["id"]
    assert second_data.get("contributor_id") == contributor_id
    assert second_data.get("clip_id") is None
    assert (
        isinstance(second_data.get("validation_error"), str)
        and second_data["validation_error"]
    )
    # Should indicate duplicate
    assert "duplicate" in second_data["validation_error"].lower()
