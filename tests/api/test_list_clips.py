from __future__ import annotations

from datetime import date, timedelta


def test_list_clips_basic_listing(client) -> None:
    # Create contributor
    contributor_resp = client.post(
        "/contributors", json={"display_name": "List Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create multiple clips with different dates
    # Use valid 11-character YouTube video IDs
    video_ids = ["test0000001", "test0000002", "test0000003"]
    dates = ["2024-01-15", "2024-02-20", "2024-03-10"]
    clip_ids = []
    for i, (video_id, date_str) in enumerate(zip(video_ids, dates)):
        submission_payload = {
            "contributor_id": contributor_id,
            "raw_youtube_input": f"https://youtu.be/{video_id}",
            "raw_date_input": date_str,
            "title": f"Performance {i}",
        }
        create_resp = client.post("/submissions", json=submission_payload)
        assert create_resp.status_code == 201, create_resp.text
        clip_id = create_resp.json()["clip_id"]
        assert clip_id is not None, "Clip should be created"
        clip_ids.append(clip_id)

    # List all clips
    list_resp = client.get("/clips")
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()

    # Verify response structure
    assert "items" in data
    assert "next_cursor" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 3

    # Verify clips are ordered by performance_date
    assert data["items"][0]["performance_date"] == "2024-01-15"
    assert data["items"][1]["performance_date"] == "2024-02-20"
    assert data["items"][2]["performance_date"] == "2024-03-10"

    # Verify clip structure
    clip = data["items"][0]
    assert "id" in clip
    assert "youtube_video_id" in clip
    assert "youtube_url" in clip
    assert "performance_date" in clip
    assert "title" in clip
    assert "created_at" in clip
    assert "created_by_contributor_id" in clip
    assert "added_via_submission_id" in clip


def test_list_clips_date_filtering_from(client) -> None:
    # Create contributor
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Filter Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create clips with different dates
    video_ids = ["filter00001", "filter00002", "filter00003"]
    dates = ["2024-01-15", "2024-02-20", "2024-03-10"]
    for video_id, date_str in zip(video_ids, dates):
        submission_payload = {
            "contributor_id": contributor_id,
            "raw_youtube_input": f"https://youtu.be/{video_id}",
            "raw_date_input": date_str,
        }
        create_resp = client.post("/submissions", json=submission_payload)
        assert create_resp.status_code == 201, create_resp.text
        assert create_resp.json()["clip_id"] is not None, "Clip should be created"

    # Filter from 2024-02-01
    list_resp = client.get("/clips", params={"from": "2024-02-01"})
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()

    assert len(data["items"]) == 2
    assert data["items"][0]["performance_date"] == "2024-02-20"
    assert data["items"][1]["performance_date"] == "2024-03-10"


def test_list_clips_date_filtering_to(client) -> None:
    # Create contributor
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Filter Tester 2", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create clips with different dates
    video_ids = ["filter200001", "filter200002", "filter200003"]
    dates = ["2024-01-15", "2024-02-20", "2024-03-10"]
    for video_id, date_str in zip(video_ids, dates):
        submission_payload = {
            "contributor_id": contributor_id,
            "raw_youtube_input": f"https://youtu.be/{video_id}",
            "raw_date_input": date_str,
        }
        create_resp = client.post("/submissions", json=submission_payload)
        assert create_resp.status_code == 201, create_resp.text
        assert create_resp.json()["clip_id"] is not None, "Clip should be created"

    # Filter to 2024-02-25
    list_resp = client.get("/clips", params={"to": "2024-02-25"})
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()

    assert len(data["items"]) == 2
    assert data["items"][0]["performance_date"] == "2024-01-15"
    assert data["items"][1]["performance_date"] == "2024-02-20"


def test_list_clips_date_filtering_range(client) -> None:
    # Create contributor
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Range Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create clips with different dates
    video_ids = ["range0000001", "range0000002", "range0000003", "range0000004"]
    dates = ["2024-01-15", "2024-02-20", "2024-03-10", "2024-04-05"]
    for video_id, date_str in zip(video_ids, dates):
        submission_payload = {
            "contributor_id": contributor_id,
            "raw_youtube_input": f"https://youtu.be/{video_id}",
            "raw_date_input": date_str,
        }
        create_resp = client.post("/submissions", json=submission_payload)
        assert create_resp.status_code == 201, create_resp.text
        assert create_resp.json()["clip_id"] is not None, "Clip should be created"

    # Filter from 2024-02-01 to 2024-03-31
    list_resp = client.get(
        "/clips", params={"from": "2024-02-01", "to": "2024-03-31"}
    )
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()

    assert len(data["items"]) == 2
    assert data["items"][0]["performance_date"] == "2024-02-20"
    assert data["items"][1]["performance_date"] == "2024-03-10"


def test_list_clips_pagination_with_cursor(client) -> None:
    # Create contributor
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Pagination Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create 5 clips
    for i in range(5):
        video_id = f"page{i:011d}"
        submission_payload = {
            "contributor_id": contributor_id,
            "raw_youtube_input": f"https://youtu.be/{video_id}",
            "raw_date_input": f"2024-01-{i+1:02d}",
        }
        create_resp = client.post("/submissions", json=submission_payload)
        assert create_resp.status_code == 201, create_resp.text
        assert create_resp.json()["clip_id"] is not None, "Clip should be created"

    # Get first page with limit 2
    list_resp = client.get("/clips", params={"limit": "2"})
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()

    assert len(data["items"]) == 2
    assert data["next_cursor"] is not None

    # Get second page using cursor
    cursor = data["next_cursor"]
    list_resp2 = client.get("/clips", params={"limit": "2", "cursor": cursor})
    assert list_resp2.status_code == 200, list_resp2.text
    data2 = list_resp2.json()

    assert len(data2["items"]) == 2
    # Verify different clips
    assert data["items"][0]["id"] != data2["items"][0]["id"]


def test_list_clips_pagination_no_more_results(client) -> None:
    # Create contributor
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Pagination Tester 2", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create 2 clips
    for i in range(2):
        video_id = f"nomore{i:011d}"
        submission_payload = {
            "contributor_id": contributor_id,
            "raw_youtube_input": f"https://youtu.be/{video_id}",
            "raw_date_input": f"2024-01-{i+1:02d}",
        }
        create_resp = client.post("/submissions", json=submission_payload)
        assert create_resp.status_code == 201, create_resp.text
        assert create_resp.json()["clip_id"] is not None, "Clip should be created"

    # Get first page with limit 2
    list_resp = client.get("/clips", params={"limit": "2"})
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()

    assert len(data["items"]) == 2
    # Should have no next cursor since we got all results
    assert data["next_cursor"] is None


def test_list_clips_limit_enforcement(client) -> None:
    # Create contributor
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Limit Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create 3 clips
    for i in range(3):
        video_id = f"limit{i:011d}"
        submission_payload = {
            "contributor_id": contributor_id,
            "raw_youtube_input": f"https://youtu.be/{video_id}",
            "raw_date_input": f"2024-01-{i+1:02d}",
        }
        create_resp = client.post("/submissions", json=submission_payload)
        assert create_resp.status_code == 201, create_resp.text
        assert create_resp.json()["clip_id"] is not None, "Clip should be created"

    # Test default limit (should be 50, but we only have 3)
    list_resp = client.get("/clips")
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()
    assert len(data["items"]) == 3

    # Test explicit limit
    list_resp2 = client.get("/clips", params={"limit": "2"})
    assert list_resp2.status_code == 200, list_resp2.text
    data2 = list_resp2.json()
    assert len(data2["items"]) == 2

    # Test max limit (200) - should not exceed
    list_resp3 = client.get("/clips", params={"limit": "500"})
    assert list_resp3.status_code == 200, list_resp3.text
    data3 = list_resp3.json()
    # Should cap at 200, but we only have 3, so should return 3
    assert len(data3["items"]) == 3


def test_list_clips_ordering_by_performance_date_then_created_at(client) -> None:
    # Create contributor
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Order Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    # Create clips with same performance date but different created_at
    # (created in sequence, so created_at will differ)
    # Use unique 11-character video IDs - use more distinct patterns
    video_ids = ["order1111111", "order2222222", "order3333333"]
    clip_ids = []
    for video_id in video_ids:
        submission_payload = {
            "contributor_id": contributor_id,
            "raw_youtube_input": f"https://youtu.be/{video_id}",
            "raw_date_input": "2024-01-15",  # Same date
        }
        create_resp = client.post("/submissions", json=submission_payload)
        assert create_resp.status_code == 201, f"Failed to create clip: {create_resp.text}"
        clip_id = create_resp.json()["clip_id"]
        assert clip_id is not None, "Clip should be created"
        clip_ids.append(clip_id)

    # List clips filtered to this date to avoid other test data
    list_resp = client.get("/clips", params={"from": "2024-01-15", "to": "2024-01-15"})
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()

    # Should have at least 3 clips with this date
    matching_clips = [item for item in data["items"] if item["performance_date"] == "2024-01-15"]
    assert len(matching_clips) >= 3, f"Expected at least 3 clips, got {len(matching_clips)}"

    # Verify ordering is stable (created_at ascending as tiebreaker)
    # Items should be in creation order
    created_ats = [item["created_at"] for item in matching_clips[:3]]
    assert created_ats == sorted(created_ats), "Clips should be ordered by created_at"


def test_list_clips_empty_results(client) -> None:
    # List clips with no data
    list_resp = client.get("/clips")
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json()

    assert data["items"] == []
    assert data["next_cursor"] is None


def test_list_clips_invalid_date_format(client) -> None:
    # Test invalid 'from' date
    resp = client.get("/clips", params={"from": "invalid-date"})
    assert resp.status_code == 400, resp.text
    assert "Invalid 'from' date format" in resp.json()["detail"]

    # Test invalid 'to' date
    resp2 = client.get("/clips", params={"to": "not-a-date"})
    assert resp2.status_code == 400, resp2.text
    assert "Invalid 'to' date format" in resp2.json()["detail"]


def test_list_clips_invalid_cursor(client) -> None:
    # Test invalid cursor
    resp = client.get("/clips", params={"cursor": "invalid-cursor"})
    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"] == "Invalid cursor"

