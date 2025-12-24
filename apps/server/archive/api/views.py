from __future__ import annotations

from datetime import datetime, timezone, date
from uuid import uuid4
from archive.models import Contributor, Clip, Submission
from django.db import transaction, IntegrityError

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


def _serialize_submission(submission: Submission) -> Dict[str, Any]:
    """Serialize a Submission model to API response format.
    
    Assumes submission has contributor and clip relationships loaded (via select_related).
    """
    return {
        "id": submission.public_id,
        "contributor_id": submission.contributor.public_id,
        "clip_id": submission.clip.public_id if submission.clip else None,
        "status": submission.status,
        "validation_error": submission.validation_error,
        "raw_youtube_input": submission.raw_youtube_input,
        "raw_date_input": submission.raw_date_input,
        "title": submission.title,
        "notes": submission.notes,
        "submitted_at": dt_to_z(submission.submitted_at),
    }


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

    # Resolve contributor by public_id
    try:
        contributor = Contributor.objects.get(public_id=payload["contributor_id"])
    except Contributor.DoesNotExist:
        return Response(
            {"detail": "Contributor not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    validation_error: str | None = None
    clip_id: str | None = None
    status_str = "accepted"
    http_status = status.HTTP_201_CREATED

    # Always create a Submission record
    try:
        # Validate required inputs first.
        performance_date = date.fromisoformat(cast(str, payload["raw_date_input"]))
        youtube_video_id = extract_youtube_video_id(
            cast(str, payload["raw_youtube_input"])
        )

        with transaction.atomic():
            # Check if clip already exists (duplicate check) - inside transaction for consistency
            existing_clip = Clip.objects.filter(
                youtube_video_id=youtube_video_id, performance_date=performance_date
            ).first()

            submission = Submission.objects.create(
                contributor=contributor,
                status=Submission.Status.REJECTED,  # Start as rejected, update if validation passes
                raw_youtube_input=payload["raw_youtube_input"],
                raw_date_input=payload["raw_date_input"],
                title=payload.get("title"),
                notes=payload.get("notes"),
            )

            if existing_clip:
                # Duplicate clip - mark submission as rejected
                status_str = "rejected"
                validation_error = "Duplicate clip: clip with this YouTube video ID and performance date already exists"
                submission.validation_error = validation_error
                submission.save()
                http_status = status.HTTP_409_CONFLICT
            else:
                # Create new clip (with try/except to handle race condition)
                try:
                    clip = Clip.objects.create(
                        contributor=contributor,
                        youtube_video_id=youtube_video_id,
                        raw_youtube_input=payload["raw_youtube_input"],
                        performance_date=performance_date,
                        title=payload.get("title"),
                        notes=payload.get("notes"),
                    )

                    # Update submission to accepted
                    submission.clip = clip
                    submission.status = Submission.Status.ACCEPTED
                    submission.validation_error = None
                    submission.save()

                    clip_id = clip.public_id
                    status_str = "accepted"
                except IntegrityError:
                    # Race condition: clip was created between our check and creation
                    status_str = "rejected"
                    validation_error = "Duplicate clip: clip with this YouTube video ID and performance date already exists"
                    submission.validation_error = validation_error
                    submission.save()
                    http_status = status.HTTP_409_CONFLICT
    except ValueError as e:
        # Validation error (invalid date or YouTube URL) - still create submission
        with transaction.atomic():
            submission = Submission.objects.create(
                contributor=contributor,
                status=Submission.Status.REJECTED,
                raw_youtube_input=payload["raw_youtube_input"],
                raw_date_input=payload["raw_date_input"],
                title=payload.get("title"),
                notes=payload.get("notes"),
            )
            status_str = "rejected"
            validation_error = str(e)
            submission.validation_error = validation_error
            submission.save()

    # Reload submission with relationships to ensure they're properly loaded
    # This avoids any issues with accessing relationships that might not be cached
    submission = Submission.objects.select_related("contributor", "clip").get(
        pk=submission.pk
    )

    return Response(
        _serialize_submission(submission),
        status=http_status,
    )


@api_view(["GET"])
def get_submission(request, submissionId: str):
    """Retrieve a submission by its public_id."""
    try:
        submission = Submission.objects.select_related("contributor", "clip").get(
            public_id=submissionId
        )
    except Submission.DoesNotExist:
        return Response(
            {"detail": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(_serialize_submission(submission), status=status.HTTP_200_OK)
