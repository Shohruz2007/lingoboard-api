from rest_framework import serializers

from assessment.domain.models import AssessmentStudentResult


class AssessmentStudentResultSerializer(serializers.ModelSerializer):
    """Serializer for student results, used by both student and admin endpoints."""
    class Meta:
        model = AssessmentStudentResult
        fields = ['id', 'user', 'assessment_section', 'score', 'explanation', 'suggestion', 'created_at', 'updated_at']
        read_only_fields = ['id']


class AssessmentStudentResultWithExtraDataSerializer(serializers.ModelSerializer):
    """Serializer for student results, used by both student and admin endpoints."""
    section_title = serializers.CharField(source='assessment_section.title', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    
    class Meta:
        model = AssessmentStudentResult
        fields = ['id', 'user', 'assessment_section', 'score', 'explanation', 'suggestion', 'created_at', 'updated_at', 'section_title', 'first_name', 'last_name']
        read_only_fields = ['id']

class AssessmentStudentResultSectionTitleSerializer(serializers.ModelSerializer):
    """Serializer for student results with section title."""
    section_title = serializers.CharField(source='assessment_section.title', read_only=True)

    class Meta:
        model = AssessmentStudentResult
        fields = [
            'id', 'user', 'assessment_section', 'section_title',
            'score', 'explanation', 'suggestion', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id']