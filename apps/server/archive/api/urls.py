from django.urls import path
from .views import create_contributor, create_submission

urlpatterns = [
    path("contributors", create_contributor),
    path("submissions", create_submission),
]
