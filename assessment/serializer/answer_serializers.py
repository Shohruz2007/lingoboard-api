from rest_framework import serializers

from assessment.domain.models import AssessmentSectionAnswer


class AssessmentSectionAnswerSerializer(serializers.ModelSerializer):
    """Serializer for AssessmentSectionAnswer model (answer key for sections)."""

    class Meta:
        model = AssessmentSectionAnswer
        fields = ['id', 'assessment_section', 'answers']
        read_only_fields = ['id']

    def validate_answers(self, value):
        # Ensure answers are provided in a correct format
        if not isinstance(value, (list, dict)):
            raise serializers.ValidationError("Answers must be a list or a dict.")
        return value
