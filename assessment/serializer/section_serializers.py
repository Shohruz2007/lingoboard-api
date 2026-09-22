from rest_framework import serializers

from assessment.domain.models import AssessmentSection


class AssessmentSectionSerializer(serializers.ModelSerializer):
    """Serializer for the AssessmentSection model."""

    class Meta:
        model = AssessmentSection
        fields = ['id', 'title', 'part_name', 'assessment', 'content_data']
        read_only_fields = ['id']
