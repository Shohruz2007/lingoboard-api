from rest_framework import serializers

from assessment.domain.models import MockExam


class MockExamAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin-facing MockExam operations."""
    end_time = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = MockExam
        fields = [
            'id', 'title',
            'time_limit_minutes', 'start_time', 'end_time', 'is_active',
            'created_at', 'updated_at', 'assessments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'end_time', 'is_active']

    def get_end_time(self, obj):
        return obj.end_time

    def get_is_active(self, obj):
        return obj.is_active()

class MockExamSerializer(serializers.ModelSerializer):
    """Serializer for student-facing MockExam operations."""

    class Meta:
        model = MockExam
        fields = [
            'id',
            'title',
            'assessments',
            'time_limit_minutes',
            'start_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'end_time', 'is_active']

    def get_end_time(self, obj):
        return obj.end_time

    def get_is_active(self, obj):
        return obj.is_active()
