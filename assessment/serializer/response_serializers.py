from rest_framework import serializers
from django.core.exceptions import ValidationError

from assessment.domain.models import (
    AssessmentStudentResponse,
    AssessmentSection,
    Assessment,
    MockExam,
)
from user.models import Lesson


class AssessmentStudentResponseSerializer(serializers.ModelSerializer):
    """Serializer for creating and reading student responses."""

    assessment_section = serializers.PrimaryKeyRelatedField(
        queryset=AssessmentSection.objects.all()
    )
    assessment = serializers.PrimaryKeyRelatedField(
        queryset=Assessment.objects.all(), required=False, allow_null=True
    )
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(), required=False, allow_null=True
    )
    mock = serializers.PrimaryKeyRelatedField(
        queryset=MockExam.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = AssessmentStudentResponse
        fields = [
            "id",
            "assessment_section",
            "answers",
            "assessment",
            "lesson",
            "mock",
        ]
        read_only_fields = ["id"]

    def validate_answers(self, value):
        if not isinstance(value, (list, dict)):
            raise serializers.ValidationError("Answers must be a list or dict.")
        return value

    def validate(self, data):
        """Validate that either lesson or mock is provided, but not both."""
        lesson = data.get("lesson")
        mock = data.get("mock")

        if not lesson and not mock:
            raise ValidationError("Either lesson or mock must be provided.")

        if lesson and mock:
            raise ValidationError("Cannot provide both lesson and mock.")

        return data
