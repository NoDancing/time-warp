from __future__ import annotations

from datetime import datetime, timezone, date
from uuid import uuid4
from archive.models import Contributor

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import re
from typing import Any, Dict, cast

from .serializers import CreateContributorRequest, CreateSubmissionRequest


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def dt_to_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


YOUTUBE_ID_RE = re.compile(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})")


def extract_youtube_video_id(raw: str) -> str:
    """Extract a YouTube video id from common URL formats.

    Accepts URLs like:
      - https://youtu.be/<id>
      - https://www.youtube.com/watch?v=<id>

    Raises ValueError if the id cannot be extracted.
    """
    m = YOUTUBE_ID_RE.search(raw or "")
    if not m:
        raise ValueError("Invalid YouTube URL or video id")
    return m.group(1)


@api_view(["POST"])
def create_contributor(request):
    ser = CreateContributorRequest(data=request.data)
    ser.is_valid(raise_exception=True)
    payload = cast(Dict[str, Any], ser.validated_data)

    contributor = Contributor.objects.create(
        display_name=payload.get("display_name"),
        external_id=payload.get("external_id"),
    )

    return Response(
        {
            "id": contributor.public_id,
            "display_name": contributor.display_name,
            "external_id": contributor.external_id,
            "created_at": dt_to_z(contributor.created_at),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def create_submission(request):
    ser = CreateSubmissionRequest(data=request.data)
    ser.is_valid(raise_exception=True)
    payload = cast(Dict[str, Any], ser.validated_data)

    validation_error: str | None = None
    clip_id: str | None = None
    status_str = "accepted"

    try:
        # Validate required inputs.
        date.fromisoformat(cast(str, payload["raw_date_input"]))
        extract_youtube_video_id(cast(str, payload["raw_youtube_input"]))

        # For now we still generate ids in-memory (DB-backed behavior comes next).
        clip_id = f"clp_{uuid4().hex}"
    except Exception as e:
        status_str = "rejected"
        validation_error = str(e)

    return Response(
        {
            "id": f"sub_{uuid4().hex}",
            "contributor_id": payload["contributor_id"],
            "clip_id": clip_id,
            "status": status_str,
            "validation_error": validation_error,
            "raw_youtube_input": payload["raw_youtube_input"],
            "raw_date_input": payload["raw_date_input"],
            "title": payload.get("title"),
            "notes": payload.get("notes"),
            "submitted_at": utc_now_z(),
        },
        status=status.HTTP_201_CREATED,
    )
