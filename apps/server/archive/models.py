from __future__ import annotations

from django.db import models
from uuid import uuid4


def new_contributor_public_id() -> str:
    return f"ctr_{uuid4().hex}"


def new_clip_public_id() -> str:
    return f"clp_{uuid4().hex}"


def new_submission_public_id() -> str:
    return f"sub_{uuid4().hex}"


class Contributor(models.Model):
    # Public contract id (what your API returns)
    public_id = models.CharField(
        max_length=40, unique=True, db_index=True, default=new_contributor_public_id
    )

    display_name = models.CharField(max_length=200, null=True, blank=True)
    external_id = models.CharField(max_length=200, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.display_name or self.public_id


class Clip(models.Model):
    # Public contract id (what your API returns)
    public_id = models.CharField(
        max_length=40, unique=True, db_index=True, default=new_clip_public_id
    )

    # canonical record
    contributor = models.ForeignKey(
        Contributor, on_delete=models.PROTECT, related_name="clips"
    )

    youtube_video_id = models.CharField(max_length=32)
    raw_youtube_input = models.TextField()

    performance_date = models.DateField()
    title = models.CharField(max_length=500, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["youtube_video_id", "performance_date"]]


class Submission(models.Model):
    class Status(models.TextChoices):
        ACCEPTED = "accepted"
        REJECTED = "rejected"

    # Public contract id (what your API returns)
    public_id = models.CharField(
        max_length=40, unique=True, db_index=True, default=new_submission_public_id
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACCEPTED,
    )

    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.PROTECT,
        related_name="submissions",
    )

    clip = models.ForeignKey(
        Clip,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )

    validation_error = models.TextField(null=True, blank=True)

    raw_youtube_input = models.TextField()
    raw_date_input = models.CharField(max_length=50)

    title = models.CharField(max_length=500, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
