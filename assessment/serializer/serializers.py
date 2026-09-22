from rest_framework import serializers
from ..domain.models import Assessment, AssessmentSection, AssessmentSectionAnswer, AssessmentStudentResponse, AssessmentStudentResult, MockExam

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id', 'type']

class AssessmentSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSection
        fields = ['id', 'title', 'part_name', 'assessment', 'content_data']

class AssessmentStudentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentStudentResult
        fields = ['id', 'user', 'assessment_section', 'score', 'explanation']

class AssessmentSectionAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssessmentSectionAnswer
        fields = ['id', 'assessment_section', 'answers']
        read_only_fields = ['id']
    
    

        
class AssessmentStudentResponseSerializer(serializers.ModelSerializer):
    assessment = serializers.IntegerField(write_only=True)
    class Meta:
        model = AssessmentStudentResponse
        fields = ['id', 'assessment_section', 'user', 'answers', 'assessment', 'stopwatch']
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        assessment = attrs.get('assessment')
        section = attrs.get('assessment_section')
        if assessment and section and section.assessment.id != assessment:
            raise serializers.ValidationError("Section does not belong to the provided assessment.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('assessment', None)
        return AssessmentStudentResponse.objects.create(**validated_data)

class MockExamAdminSerializer(serializers.ModelSerializer):
    end_time = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = MockExam
        fields = [
            'id', 'title',
            'time_limit_minutes', 'start_time', 'end_time', 'is_active',
            'created_at', 'updated_at', 'assessments'
        ]

    def get_end_time(self, obj):
        return obj.end_time

    def get_is_active(self, obj):
        return obj.is_active()