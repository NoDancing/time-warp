# Minimal API stub to satisfy the first contract test

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# Models the expected request body for POST /contributors
class CreateContributorRequest(BaseModel):
    display_name: str | None = None
    external_id: str | None = None


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
