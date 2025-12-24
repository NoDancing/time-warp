# Minimal API stub to satisfy the first contract test

from __future__ import annotations

from datetime import datetime, timezone, date
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# Models the expected request body for POST /contributors
class CreateContributorRequest(BaseModel):
    display_name: str | None = None
    external_id: str | None = None


# Models the expected request body for POST /submissions
class CreateSubmissionRequest(BaseModel):
    contributor_id: str
    raw_youtube_input: str
    raw_date_input: str
    title: str | None = None
    notes: str | None = None


# Initializes the FastAPI application
app = FastAPI(title="Time Warp API")


@app.post("/contributors")
def create_contributor(payload: CreateContributorRequest) -> JSONResponse:
    contributor = {
        "id": f"ctr_{uuid4().hex}",
        "display_name": payload.display_name,
        "external_id": payload.external_id,
        # Generate the current UTC timestamp formatted with a trailing 'Z' to indicate UTC
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    # Return the contributor data with HTTP status 201 Created
    return JSONResponse(status_code=201, content=contributor)


@app.post("/submissions")
def create_submission(payload: CreateSubmissionRequest) -> JSONResponse:
    # Minimal validation: ensure the date parses as YYYY-MM-DD.
    # Rejection handling will be added later via tests.
    date.fromisoformat(payload.raw_date_input)

    submission = {
        "id": f"sub_{uuid4().hex}",
        "contributor_id": payload.contributor_id,
        "clip_id": f"clp_{uuid4().hex}",
        "status": "accepted",
        "validation_error": None,
        "raw_youtube_input": payload.raw_youtube_input,
        "raw_date_input": payload.raw_date_input,
        "title": payload.title,
        "notes": payload.notes,
        "submitted_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return JSONResponse(status_code=201, content=submission)
