from rest_framework import viewsets, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from LingoBoard.pagination import StandardResultsSetPagination
from assessment.domain.models import (
    Assessment,
    AssessmentSectionAnswer,
    AssessmentStudentResult,
    MockExam,
    ProgressTrack,
)
from assessment.serializer.assessment_serializers import AssessmentSerializer
from assessment.serializer.answer_serializers import AssessmentSectionAnswerSerializer
from assessment.serializer.result_serializers import (
    AssessmentStudentResultSerializer,
    AssessmentStudentResultWithExtraDataSerializer,
)
from assessment.serializer.mock_exam_serializers import MockExamAdminSerializer
from assessment.serializer.progress_serializers import ProgressTrackDetailSerializer
from LingoBoard.permission import TeacherStatusPermission
from assessment.service.result_service import ResultUpdateService
from assessment.service.mock_exam_service import MockExamService

import logging
from django.db.models import Q

logger = logging.getLogger(__name__)


class AssessmentResultFilter(django_filters.FilterSet):
    """
    Custom filter for AssessmentStudentResult with lesson filtering support.
    """

    lesson = django_filters.NumberFilter(
        method="filter_by_lesson", help_text="Filter results by lesson ID"
    )

    def filter_by_lesson(self, queryset, name, value):
        """
        Filter results by lesson ID through the relationship chain:
        Lesson -> Assessment -> AssessmentSection -> AssessmentStudentResult
        """
        if value:
            return queryset.filter(assessment_section__assessment__assessments__id=value).distinct()
        return queryset

    class Meta:
        model = AssessmentStudentResult
        fields = ["assessment_section", "user", "lesson"]


class AssessmentModelViewSet(viewsets.ModelViewSet):
    """
    CRUD for Assessments (teachers only).
    """

    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [TeacherStatusPermission]


class AssessmentSectionAnswerModelViewSet(viewsets.ModelViewSet):
    """
    CRUD for section answer keys (teachers only).
    """

    queryset = AssessmentSectionAnswer.objects.all()
    serializer_class = AssessmentSectionAnswerSerializer
    permission_classes = [TeacherStatusPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["assessment_section"]


class AssessmentStudentResultUpdateView(generics.UpdateAPIView):
    """
    Update a student's result and recalculate overall status.
    """

    serializer_class = AssessmentStudentResultSerializer
    permission_classes = [TeacherStatusPermission]
    result_service = ResultUpdateService()

    def get_object(self):
        user_id = self.request.query_params.get("user")
        section_id = self.request.query_params.get("assessment_section")
        return self.result_service.get_result_or_404(user_id, section_id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        updated = self.result_service.update_score_and_status(
            result=instance, new_data=request.data
        )

        return Response(self.get_serializer(updated).data)


class AssessmentAdminResultListView(viewsets.ReadOnlyModelViewSet):
    """
    List all student results, with filtering/search (teachers only).
    """

    queryset = (
        AssessmentStudentResult.objects.prefetch_related(
            "assessment_section", "user", "assessment_section__assessment__assessments"
        )
        .only(
            "id",
            "user_id",
            "assessment_section_id",
            "score",
            "explanation",
            "suggestion",
            "created_at",
            "updated_at",
            "assessment_section__title",
            "assessment_section__assessment__assessments__id",
            "user__first_name",
            "user__last_name",
        )
        .order_by("-created_at")
    )
    serializer_class = AssessmentStudentResultWithExtraDataSerializer
    permission_classes = [TeacherStatusPermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    pagination_class = StandardResultsSetPagination
    filterset_class = AssessmentResultFilter
    search_fields = [
        "assessment_section__title",
        "user__username",
        "user__first_name",
        "user__last_name",
    ]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def list(self, request, *args, **kwargs):
        try:
            # Debug pagination parameters
            logger.info(
                f"Pagination params: page={request.query_params.get('page')}, page_size={request.query_params.get('page_size')}"
            )
            logger.info(f"Pagination class: {self.pagination_class}")
            logger.info(f"Has paginator: {hasattr(self, 'paginator')}")

            logger.info("Getting fresh response from database")
            response = super().list(request, *args, **kwargs)

            # Debug response data
            logger.info(f"Response data type: {type(response.data)}")
            if hasattr(response.data, "get"):
                logger.info(
                    f"Response keys: {list(response.data.keys()) if response.data else 'None'}"
                )
                if response.data and "results" in response.data:
                    logger.info(f"Results count: {len(response.data['results'])}")
                    logger.info(f"Next page: {response.data.get('next')}")
                    logger.info(f"Previous page: {response.data.get('previous')}")

            return response

        except Exception as e:
            logger.error(f"Error in list method: {e}")
            # Fallback to normal response without caching
            return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """Override to add cache warming for frequently accessed queries"""
        try:
            queryset = super().get_queryset()

            # Optimize for lesson filtering if lesson parameter is present
            lesson_param = self.request.query_params.get("lesson")
            if lesson_param:
                # Add prefetch for lesson relationship when filtering by lesson
                queryset = queryset.prefetch_related(
                    "assessment_section__assessment__assessments"
                )

            graded_param = self.request.query_params.get("graded")
            if graded_param is not None:
                is_false = str(graded_param).lower() in ("false", "0", "no")
                if is_false:
                    queryset = queryset.filter(Q(score__isnull=True) | Q(score=""))
                else:
                    queryset = queryset.exclude(score__isnull=True).exclude(score="")
            return queryset
        except Exception as e:
            logger.error(f"Error in get_queryset: {e}")
            return super().get_queryset()


class MockExamAdminViewSet(viewsets.ModelViewSet):
    """
    CRUD + custom actions for Mock Exams (teachers only).
    """

    queryset = MockExam.objects.all().prefetch_related("assessments")
    serializer_class = MockExamAdminSerializer
    permission_classes = [TeacherStatusPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["title"]
    search_fields = ["title", "description"]
    exam_service = MockExamService()

    @action(detail=True, methods=["post"], url_path="start-now")
    def start_now(self, request, pk=None):
        payload = self.exam_service.start_now(mock_exam_id=pk)
        return Response(payload)

    @action(detail=True, methods=["post"], url_path="force-close")
    def force_close(self, request, pk=None):
        payload = self.exam_service.force_close(mock_exam_id=pk)
        return Response(payload)


class AdminProgressLessonView(generics.ListAPIView):
    """
    List all lesson progress tracking with admin-level filtering capabilities.
    Teachers can view lesson progress for all students.
    Requires student_id parameter to filter by specific student.
    """

    serializer_class = ProgressTrackDetailSerializer
    permission_classes = [TeacherStatusPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["user", "lesson_id"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "assessment__type",
        "lesson_id__title",
    ]
    ordering_fields = ["created_at", "updated_at", "user__username"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        queryset = (
            ProgressTrack.objects.select_related("user", "lesson_id", "mock_id")
            .prefetch_related("assessment", "section_list", "result_list")
            .filter(lesson_id__isnull=False)
        )

        # Filter by specific student - required for admin
        student_id = self.request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(user_id=student_id)
        else:
            # If no student_id provided, return empty queryset
            queryset = queryset.none()

        # Filter by lesson_id if provided
        lesson_id = self.request.query_params.get("lesson_id")
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)

        return queryset


class AdminProgressMockView(generics.ListAPIView):
    """
    List all mock exam progress tracking with admin-level filtering capabilities.
    Teachers can view mock exam progress for all students.
    Requires student_id parameter to filter by specific student.
    """

    serializer_class = ProgressTrackDetailSerializer
    permission_classes = [TeacherStatusPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["user", "mock_id"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "assessment__type",
        "mock_id__title",
    ]
    ordering_fields = ["created_at", "updated_at", "user__username"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        queryset = (
            ProgressTrack.objects.select_related("user", "lesson_id", "mock_id")
            .prefetch_related("assessment", "section_list", "result_list")
            .filter(mock_id__isnull=False)
        )

        # Filter by specific student - required for admin
        student_id = self.request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(user_id=student_id)
        else:
            # If no student_id provided, return empty queryset
            queryset = queryset.none()

        # Filter by mock_id if provided
        mock_id = self.request.query_params.get("mock_id")
        if mock_id:
            queryset = queryset.filter(mock_id=mock_id)

        return queryset
