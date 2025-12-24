from django.urls import path
from .views import (
    create_contributor,
    create_submission,
    get_submission,
    get_clip,
    list_clips,
)

urlpatterns = [
    path("contributors", create_contributor),
    path("submissions", create_submission),
    path("submissions/<str:submissionId>", get_submission),
    path("clips", list_clips),
    path("clips/<str:clipId>", get_clip),
]
