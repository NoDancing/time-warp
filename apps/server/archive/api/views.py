from __future__ import annotations

from datetime import datetime, timezone, date
from uuid import uuid4

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import CreateContributorRequest, CreateSubmissionRequest


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@api_view(["POST"])
def create_contributor(request):
    ser = CreateContributorRequest(data=request.data)
    ser.is_valid(raise_exception=True)
    payload = ser.validated_data

    return Response(
        {
            "id": f"ctr_{uuid4().hex}",
            "display_name": payload.get("display_name"),
            "external_id": payload.get("external_id"),
            "created_at": utc_now_z(),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def create_submission(request):
    ser = CreateSubmissionRequest(data=request.data)
    ser.is_valid(raise_exception=True)
    payload = ser.validated_data

    # minimal contract validation: must parse YYYY-MM-DD
    date.fromisoformat(payload["raw_date_input"])

    return Response(
        {
            "id": f"sub_{uuid4().hex}",
            "contributor_id": payload["contributor_id"],
            "clip_id": f"clp_{uuid4().hex}",
            "status": "accepted",
            "validation_error": None,
            "raw_youtube_input": payload["raw_youtube_input"],
            "raw_date_input": payload["raw_date_input"],
            "title": payload.get("title"),
            "notes": payload.get("notes"),
            "submitted_at": utc_now_z(),
        },
        status=status.HTTP_201_CREATED,
    )