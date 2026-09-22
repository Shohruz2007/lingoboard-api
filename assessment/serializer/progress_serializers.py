from rest_framework import serializers
from user.serializers import UserProfileSerializer
from assessment.domain.models import (
    ProgressTrack,
    Assessment,
    AssessmentSection,
    AssessmentStudentResult,
)
from user.models import Lesson


class ProgressTrackSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    assessment = serializers.StringRelatedField(many=True, read_only=True)
    lesson_id = serializers.StringRelatedField(read_only=True)
    mock_id = serializers.StringRelatedField(read_only=True)
    section_list = serializers.StringRelatedField(many=True, read_only=True)
    result_list = serializers.StringRelatedField(many=True, read_only=True)

    # Computed field to show the context (lesson or mock)
    context_type = serializers.SerializerMethodField()
    context_title = serializers.SerializerMethodField()

    class Meta:
        model = ProgressTrack
        fields = [
            "id",
            "user",
            "assessment",
            "lesson_id",
            "mock_id",
            "context_type",
            "context_title",
            "section_list",
            "result_list",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id"]

    def get_context_type(self, obj):
        return "lesson" if obj.lesson_id else "mock"

    def get_context_title(self, obj):
        return obj.lesson_id.title if obj.lesson_id else obj.mock_id.title


class ProgressTrackDetailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    assessment = serializers.StringRelatedField(many=True, read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(read_only=True)
    mock_id = serializers.PrimaryKeyRelatedField(read_only=True)
    section_list = serializers.StringRelatedField(many=True, read_only=True)
    result_list = serializers.StringRelatedField(many=True, read_only=True)

    # Additional computed fields
    context_type = serializers.SerializerMethodField()
    context_title = serializers.SerializerMethodField()
    total_sections = serializers.SerializerMethodField()
    completed_sections = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = ProgressTrack
        fields = [
            "id",
            "user",
            "assessment",
            "lesson_id",
            "mock_id",
            "context_type",
            "context_title",
            "section_list",
            "result_list",
            "total_sections",
            "completed_sections",
            "progress_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id"]

    def get_context_type(self, obj):
        return "lesson" if obj.lesson_id else "mock"

    def get_context_title(self, obj):
        return obj.lesson_id.title if obj.lesson_id else obj.mock_id.title

    def get_total_sections(self, obj):
        return obj.section_list.count()

    def get_completed_sections(self, obj):
        return obj.result_list.count()

    def get_progress_percentage(self, obj):
        total = self.get_total_sections(obj)
        if total == 0:
            return 0
        completed = self.get_completed_sections(obj)
        return round((completed / total) * 100, 2)
