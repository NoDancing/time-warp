from __future__ import annotations

from datetime import datetime, timezone, date
from uuid import uuid4
from typing import Any, Dict, cast

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import CreateContributorRequest, CreateSubmissionRequest


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@api_view(["POST"])
def create_contributor(request):
    ser = CreateContributorRequest(data=request.data)
    ser.is_valid(raise_exception=True)
    payload = cast(Dict[str, Any], ser.validated_data)

    contributor = {
        "id": f"ctr_{uuid4().hex}",
        "display_name": payload.get("display_name", None),
        "external_id": payload.get("external_id", None),
        "created_at": utc_now_z(),
    }
    return Response(contributor, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def create_submission(request):
    ser = CreateSubmissionRequest(data=request.data)
    ser.is_valid(raise_exception=True)
    payload = cast(Dict[str, Any], ser.validated_data)

    # Minimal validation: ensure date parses as YYYY-MM-DD.
    # (Rejection behavior will come later, via tests.)
    date.fromisoformat(payload["raw_date_input"])

    submission = {
        "id": f"sub_{uuid4().hex}",
        "contributor_id": payload["contributor_id"],
        "clip_id": f"clp_{uuid4().hex}",
        "status": "accepted",
        "validation_error": None,
        "raw_youtube_input": payload["raw_youtube_input"],
        "raw_date_input": payload["raw_date_input"],
        "title": payload.get("title", None),
        "notes": payload.get("notes", None),
        "submitted_at": utc_now_z(),
    }
    return Response(submission, status=status.HTTP_201_CREATED)