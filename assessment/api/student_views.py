from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from LingoBoard.pagination import StandardResultsSetPagination
from assessment.domain.models import (
    AssessmentSection,
    AssessmentStudentResponse,
    AssessmentStudentResult,
    ProgressTrack,
    MockExam,
)
from assessment.serializer.mock_exam_serializers import MockExamSerializer
from assessment.serializer.section_serializers import AssessmentSectionSerializer
from assessment.serializer.response_serializers import (
    AssessmentStudentResponseSerializer,
)
from assessment.serializer.result_serializers import (
    AssessmentStudentResultSectionTitleSerializer,
    AssessmentStudentResultSerializer,
)
from assessment.serializer.progress_serializers import ProgressTrackDetailSerializer
from LingoBoard.permission import TeacherStatusPermission

from assessment.service.assessment_access_service import AssessmentAccessService
from assessment.service.submission_service import SubmissionService
from assessment.service.result_service import StudentResultService
from assessment.service.mock_exam_service import MockExamService
from assessment.service.progress_track_service import ProgressTrackService

from assessment.selector.assessment_selectors import get_correct_answers


class AssessmentSectionsByAssessmentReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List sections for a given assessment, along with the student's progress/status.
    """

    serializer_class = AssessmentSectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    access_service = AssessmentAccessService()

    def list(self, request, *args, **kwargs):
        assessment_id = self.kwargs["assessment_id"]
        payload = self.access_service.get_sections_payload(
            assessment_id=assessment_id, user=request.user
        )
        return Response(payload)

    def retrieve(self, request, *args, **kwargs):
        # Let DRF handle the retrieve; serializer just returns the section data
        return super().retrieve(request, *args, **kwargs)


class AssessmentStudentResponseCreate(generics.CreateAPIView):
    """
    Submit answers for a section; grading, results, status updates, and progress tracking are handled in the service.
    """

    serializer_class = AssessmentStudentResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    submission_service = SubmissionService()
    progress_track_service = ProgressTrackService()

    def perform_create(self, serializer):
        user = self.request.user
        section = serializer.validated_data["assessment_section"]
        answers = serializer.validated_data["answers"]
        assessment = serializer.validated_data.get("assessment")
        lesson = serializer.validated_data.get("lesson")
        mock = serializer.validated_data.get("mock")

        # Delegates the entire workflow (response, grading, status update)
        self.submission_service.submit_section(
            user=user, section=section, answers=answers
        )

        # Update progress tracking
        if assessment and (lesson or mock):
            self.progress_track_service.update_progress_track(
                user=user,
                assessment=assessment,
                section=section,
                lesson_id=lesson,
                mock_id=mock,
            )


class AssessmentStudentResponseReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read student responses; teachers/admins see all and get right answers.
    """

    queryset = AssessmentStudentResponse.objects.all()
    serializer_class = AssessmentStudentResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["assessment_section", "user"]

    def get_queryset(self):
        user = self.request.user
        if TeacherStatusPermission().has_permission(self.request, self):
            return super().get_queryset()
        return self.queryset.filter(user=user)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        data = {"results": self.get_serializer(qs, many=True).data}

        section_id = request.query_params.get("assessment_section")
        if section_id:
            correct = get_correct_answers(section_id)
            data["right_answers"] = correct

        return Response(data)


class AssessmentStudentResultListView(generics.ListAPIView):
    """
    List final results for a graded assessment; only after full grading.
    """

    serializer_class = AssessmentStudentResultSectionTitleSerializer
    permission_classes = [permissions.IsAuthenticated]
    result_service = StudentResultService()
    pagination_class = StandardResultsSetPagination

    ordering_fields = ["created_at", "updated_at"]
    default_ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        assessment_id = self.request.query_params.get("assessment_id")

        if assessment_id:
            return self.result_service.get_user_results_by_assessment(
                user=user, assessment_id=assessment_id
            )
        return self.result_service.get_user_results(user=user)


class MockExamViewRetrieve(generics.GenericAPIView):
    """
    Entry point for a user to get data about, start or continue a mock exam.
    """

    serializer_class = MockExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    exam_service = MockExamService()

    def get(self, request):
        """
        Handle GET request a mock exam.
        """
        mock_exam_id = self.request.get("mock_exam_id")
        if not mock_exam_id:
            return Response({"detail": "Mock exam ID is required."}, status=400)
        payload = self.exam_service.get_mock_exam(mock_exam_id)
        data = MockExamSerializer(payload).data

        return Response(data)


class MockExamViewListPost(generics.GenericAPIView):
    """
    Entry point for a user to get data about, start or continue a mock exam.
    """

    serializer_class = MockExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    exam_service = MockExamService()

    def get(self, request):
        """
        List all mock exams available to the user.
        """
        exams = self.exam_service.get_mock_exams_all()
        data = MockExamSerializer(exams, many=True).data
        return Response(data)

    def post(self, request, mock_exam_id):
        payload = self.exam_service.access_exam(
            user=request.user, mock_exam_id=mock_exam_id
        )
        return Response(payload)


class StudentMockExamResultsListView(generics.ListAPIView):
    """
    List all results for assessments under a specific mock exam belonging to the requesting user.
    """

    serializer_class = AssessmentStudentResultSectionTitleSerializer
    permission_classes = [permissions.IsAuthenticated]
    result_service = StudentResultService()
    pagination_class = StandardResultsSetPagination

    ordering_fields = ["created_at", "updated_at"]
    default_ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        return self.result_service.get_user_results_by_mock_exam(user=user)


class StudentProgressLessonView(generics.ListAPIView):
    """
    List progress tracking for lessons for the authenticated student.
    If lesson_id is provided, shows progress for that specific lesson.
    If no lesson_id is provided, shows progress for all lessons.
    """

    serializer_class = ProgressTrackDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["lesson_id"]

    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            ProgressTrack.objects.select_related("user", "lesson_id", "mock_id")
            .prefetch_related("assessment", "section_list", "result_list")
            .filter(user=user, lesson_id__isnull=False)
        )

        # Filter by lesson_id if provided
        lesson_id = self.request.query_params.get("lesson_id")
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)

        return queryset


class StudentProgressMockView(generics.ListAPIView):
    """
    List progress tracking for mock exams for the authenticated student.
    If mock_id is provided, shows progress for that specific mock exam.
    If no mock_id is provided, shows progress for all mock exams.
    """

    serializer_class = ProgressTrackDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["mock_id"]

    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            ProgressTrack.objects.select_related("user", "lesson_id", "mock_id")
            .prefetch_related("assessment", "section_list", "result_list")
            .filter(user=user, mock_id__isnull=False)
        )

        # Filter by mock_id if provided
        mock_id = self.request.query_params.get("mock_id")
        if mock_id:
            queryset = queryset.filter(mock_id=mock_id)

        return queryset
