from django.urls import include, path

urlpatterns = [
    path("", include("archive.api.urls")),
]