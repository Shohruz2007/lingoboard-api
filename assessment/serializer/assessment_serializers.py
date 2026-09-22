from rest_framework import serializers

from assessment.domain.models import Assessment


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for the Assessment model."""

    class Meta:
        model = Assessment
        fields = ['id', 'type']
        read_only_fields = ['id']
