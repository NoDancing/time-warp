def test_create_submission_invalid_youtube_is_rejected(client) -> None:
    contributor_resp = client.post(
        "/contributors", json={"display_name": "Tester", "external_id": None}
    )
    assert contributor_resp.status_code == 201, contributor_resp.text
    contributor_id = contributor_resp.json()["id"]

    payload = {
        "contributor_id": contributor_id,
        "raw_youtube_input": "not a url",
        "raw_date_input": "2024-05-12",
        "title": "Bad YouTube",
        "notes": "Should reject",
    }

    resp = client.post("/submissions", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data["status"] == "rejected"
    assert data.get("clip_id") is None
    assert isinstance(data.get("validation_error"), str) and data["validation_error"]
