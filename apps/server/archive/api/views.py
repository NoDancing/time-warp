from __future__ import annotations

from datetime import datetime, timezone, date
from uuid import uuid4
from archive.models import Contributor, Clip, Submission
from django.db import transaction, IntegrityError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import re
import base64
import json
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


def _serialize_clip(clip: Clip) -> Dict[str, Any]:
    """Serialize a Clip model to API response format.
    
    Assumes clip has contributor relationship loaded (via select_related).
    Finds the submission that created this clip.
    """
    # Find the submission that created this clip (first accepted submission)
    submission = clip.submissions.filter(status=Submission.Status.ACCEPTED).first()
    added_via_submission_id = submission.public_id if submission else None
    
    # Construct YouTube URL
    youtube_url = f"https://www.youtube.com/watch?v={clip.youtube_video_id}"
    
    return {
        "id": clip.public_id,
        "youtube_video_id": clip.youtube_video_id,
        "youtube_url": youtube_url,
        "performance_date": clip.performance_date.isoformat(),
        "title": clip.title or "",
        "notes": clip.notes,
        "created_at": dt_to_z(clip.created_at),
        "created_by_contributor_id": clip.contributor.public_id,
        "added_via_submission_id": added_via_submission_id,
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


@api_view(["GET"])
def get_clip(request, clipId: str):
    """Retrieve a clip by its public_id."""
    try:
        clip = Clip.objects.select_related("contributor").get(public_id=clipId)
    except Clip.DoesNotExist:
        return Response(
            {"detail": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(_serialize_clip(clip), status=status.HTTP_200_OK)


def _encode_cursor(offset: int) -> str:
    """Encode an offset into a cursor string."""
    data = json.dumps({"offset": offset}).encode("utf-8")
    return base64.urlsafe_b64encode(data).decode("utf-8")


def _decode_cursor(cursor: str) -> int | None:
    """Decode a cursor string to an offset. Returns None if invalid."""
    try:
        data = base64.urlsafe_b64decode(cursor.encode("utf-8"))
        decoded = json.loads(data)
        offset = decoded.get("offset")
        if isinstance(offset, int) and offset >= 0:
            return offset
    except (ValueError, json.JSONDecodeError, KeyError, TypeError):
        pass
    return None


@api_view(["GET"])
def list_clips(request):
    """List clips ordered by performance_date with optional date filtering and pagination."""
    # Parse query parameters
    from_date_str = request.query_params.get("from")
    to_date_str = request.query_params.get("to")
    limit_str = request.query_params.get("limit", "50")
    cursor_str = request.query_params.get("cursor")
    
    # Validate and parse dates
    from_date = None
    to_date = None
    if from_date_str:
        try:
            from_date = date.fromisoformat(from_date_str)
        except ValueError:
            return Response(
                {"detail": "Invalid 'from' date format. Expected YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    if to_date_str:
        try:
            to_date = date.fromisoformat(to_date_str)
        except ValueError:
            return Response(
                {"detail": "Invalid 'to' date format. Expected YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    # Validate limit
    try:
        limit = int(limit_str)
        if limit < 1:
            limit = 50
        elif limit > 200:
            limit = 200
    except ValueError:
        limit = 50
    
    # Decode cursor
    offset = 0
    if cursor_str:
        decoded_offset = _decode_cursor(cursor_str)
        if decoded_offset is None:
            return Response(
                {"detail": "Invalid cursor"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        offset = decoded_offset
    
    # Build queryset
    queryset = Clip.objects.select_related("contributor").order_by(
        "performance_date", "created_at", "id"
    )
    
    # Apply date filtering
    if from_date:
        queryset = queryset.filter(performance_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(performance_date__lte=to_date)
    
    # Get total count for pagination
    total_count = queryset.count()
    
    # Apply pagination
    clips = list(queryset[offset : offset + limit + 1])  # Fetch one extra to check if there's more
    
    # Determine if there's a next page
    has_next = len(clips) > limit
    if has_next:
        clips = clips[:limit]
    
    # Serialize clips
    items = [_serialize_clip(clip) for clip in clips]
    
    # Generate next cursor
    next_cursor = None
    if has_next:
        next_cursor = _encode_cursor(offset + limit)
    
    return Response(
        {
            "items": items,
            "next_cursor": next_cursor,
        },
        status=status.HTTP_200_OK,
    )
