from rest_framework import serializers


class CreateContributorRequest(serializers.Serializer):
    display_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    external_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class CreateSubmissionRequest(serializers.Serializer):
    contributor_id = serializers.CharField()
    raw_youtube_input = serializers.CharField()
    raw_date_input = serializers.CharField()
    title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)