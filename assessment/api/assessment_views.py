from rest_framework import viewsets, permissions

from assessment.domain.models import Assessment, AssessmentSection
from assessment.serializer.assessment_serializers import AssessmentSerializer
from assessment.serializer.section_serializers import AssessmentSectionSerializer
from assessment.selector.assessment_selectors import get_assessments_for_lesson, get_assessments_for_mock
from LingoBoard.permission import TeacherStatusPermission
from django_filters.rest_framework import DjangoFilterBackend


class AssessmentByLessonReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset to list assessments scoped to a given lesson.
    """
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        lesson_id = self.kwargs.get('lesson_id')
        if not lesson_id:
            return Assessment.objects.none()
        return get_assessments_for_lesson(lesson_id)


class AssessmentSectionModelViewSet(viewsets.ModelViewSet):
    """
    CRUD for AssessmentSections (teachers only).
    """

    queryset = AssessmentSection.objects.all()
    serializer_class = AssessmentSectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title", "part_name", "assessment"]
    search_fields = ["title", "part_name"]

class AssessmentByMockReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset to list assessments scoped to a given mock exam.
    """
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        mock_id = self.kwargs.get('mock_exam_id')
        if mock_id:
            return get_assessments_for_mock(mock_id)
        return Assessment.objects.none()

class AssessmentModelViewSet(viewsets.ModelViewSet):
    """
    Full CRUD viewset for assessments (teachers only).
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [TeacherStatusPermission]
