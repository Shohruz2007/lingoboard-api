from django.urls import path, include
from rest_framework.routers import DefaultRouter

from assessment.api.assessment_views import (
    AssessmentByLessonReadOnlyViewSet,
    AssessmentByMockReadOnlyViewSet,
    AssessmentModelViewSet,
    AssessmentSectionModelViewSet,
)
from assessment.api.student_views import (
    AssessmentSectionsByAssessmentReadOnlyViewSet,
    AssessmentStudentResponseCreate,
    AssessmentStudentResponseReadOnlyViewSet,
    AssessmentStudentResultListView,
    StudentMockExamResultsListView,
    MockExamViewRetrieve,
    MockExamViewListPost,
    StudentProgressLessonView,
    StudentProgressMockView,
)
from assessment.api.admin_views import (
    AssessmentSectionAnswerModelViewSet,
    AssessmentStudentResultUpdateView,
    AssessmentAdminResultListView,
    MockExamAdminViewSet,
    AdminProgressLessonView,
    AdminProgressMockView,
)

router = DefaultRouter()
router.register(
    r"get/by-lesson/(?P<lesson_id>[^/.]+)",
    AssessmentByLessonReadOnlyViewSet,
    basename="assessment-by-lesson",
)
router.register(
    r"get/by-mock/(?P<mock_exam_id>[^/.]+)",
    AssessmentByMockReadOnlyViewSet,
    basename="assessment-by-mock",
)
router.register(
    r"get/section-by-assessment/(?P<assessment_id>[^/.]+)/section",
    AssessmentSectionsByAssessmentReadOnlyViewSet,
    basename="assessment-sections-by-assessment",
)
router.register(
    r"sections", AssessmentSectionModelViewSet, basename="assessment-section"
)
router.register(
    r"answer", AssessmentSectionAnswerModelViewSet, basename="assessment-section-answer"
)
router.register(r"results", AssessmentAdminResultListView, basename="admin-results")
router.register(r"admin/mock-exams", MockExamAdminViewSet, basename="admin-mock-exam")
router.register(
    r"student/response/get",
    AssessmentStudentResponseReadOnlyViewSet,
    basename="student-response-get",
)
router.register(r"", AssessmentModelViewSet, basename="assessment")

urlpatterns = [
    path(
        "student/response/",
        AssessmentStudentResponseCreate.as_view(),
        name="student-response",
    ),
    path(
        "student/score-update/",
        AssessmentStudentResultUpdateView.as_view(),
        name="student-score-update",
    ),
    path(
        "get/results/",
        AssessmentStudentResultListView.as_view(),
        name="student-results",
    ),
    path(
        "get/results/by-mock/",
        StudentMockExamResultsListView.as_view(),
        name="student-results-by-mock",
    ),
    path(
        "student/progress/lesson/",
        StudentProgressLessonView.as_view(),
        name="student-progress-lesson",
    ),
    path(
        "student/progress/mock/",
        StudentProgressMockView.as_view(),
        name="student-progress-mock",
    ),
    path(
        "admin/progress/lesson/",
        AdminProgressLessonView.as_view(),
        name="admin-progress-lesson",
    ),
    path(
        "admin/progress/mock/",
        AdminProgressMockView.as_view(),
        name="admin-progress-mock",
    ),
    path(
        "mock-exam/<int:mock_exam_id>/",
        MockExamViewRetrieve.as_view(),
        name="mock-exam-retrieve",
    ),
    path("mock-exam/", MockExamViewListPost.as_view(), name="mock-exam-list-post"),
    path("", include(router.urls)),
]
