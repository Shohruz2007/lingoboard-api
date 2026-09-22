from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import F

from assessment.domain.models import AssessmentStudentResult, AssessmentStudentStatus, MockExam
from assessment.selector.result_selectors import get_user_results, get_result_by_section
from assessment.service.status_service import StatusService


class StudentResultService:
    ALLOWED_STATUSES = (
        AssessmentStudentStatus.GRADED,
        AssessmentStudentStatus.IN_PROGRESS,
    )

    def get_user_results_by_assessment(self, user, assessment_id: int):
        # Normalize/validate assessment_id from query params (string → int)
        try:
            assessment_id = int(assessment_id)
        except (TypeError, ValueError):
            raise ValidationError({"assessment_id": "Must be an integer."})

        status = (
            AssessmentStudentStatus.objects.filter(
                user=user, assessment_id=assessment_id
            )
            .select_related("assessment")
            .prefetch_related("completed_sections")
            .first()
        )
        if not status:
            raise NotFound("No assessment status found for the user and assessment.")
        if status.status not in self.ALLOWED_STATUSES:
            raise NotFound("Assessment is not graded yet.")

        section_ids = status.completed_sections.values_list("id", flat=True)
        results = AssessmentStudentResult.objects.filter(
            user=user, assessment_section_id__in=section_ids
        ).select_related("assessment_section", "assessment_section__assessment", "user")
        if not results.exists():
            raise NotFound("No results found for the given assessment section.")
        return results

    def get_user_results(self, user):
        statuses = (
            AssessmentStudentStatus.objects.filter(
                user=user, status__in=self.ALLOWED_STATUSES
            )
            .select_related("assessment")
            .prefetch_related("completed_sections")
        )
        if not statuses.exists():
            raise NotFound("No assessment status found for this user.")

        section_ids = {
            sid
            for s in statuses
            for sid in s.completed_sections.values_list("id", flat=True)
        }
        if not section_ids:
            raise NotFound("No completed sections found for this user.")

        results = AssessmentStudentResult.objects.filter(
            user=user, assessment_section_id__in=section_ids
        ).select_related("assessment_section", "assessment_section__assessment", "user")
        if not results.exists():
            raise NotFound("No results found for the completed sections.")
        return results

    def get_user_results_by_mock_exam(self, user):
        """
        Return all results of all mock exams related to the user.
        """
        # Get all assessments that are part of any mock exam
        assessment_ids = MockExam.objects.values_list("assessments__id", flat=True).distinct()
        assessment_ids = [aid for aid in assessment_ids if aid is not None]
        if not assessment_ids:
            raise NotFound("No assessments linked to any mock exam.")

        results = (
            AssessmentStudentResult.objects.filter(
                user=user,
                assessment_section__assessment_id__in=assessment_ids,
            )
            .select_related("assessment_section", "assessment_section__assessment", "user")
            .order_by("-created_at")
        )
        if not results.exists():
            raise NotFound("No results found for any mock exam for this user.")
        return results


class ResultUpdateService:
    """
    Service to update an instructor's adjustment of a student's result and cascade status.
    """

    def __init__(self):
        self.status_service = StatusService()

    def get_result_or_404(self, user_id, section_id):
        try:
            return AssessmentStudentResult.objects.get(
                user_id=user_id, assessment_section_id=section_id
            )
        except AssessmentStudentResult.DoesNotExist:
            raise NotFound("Result not found for the given user and section.")

    def update_score_and_status(self, result, new_data):
        # Update allowed fields
        for field in ("score", "explanation", "suggestion"):
            if field in new_data:
                setattr(result, field, new_data[field])
        result.save()

        # Recompute and persist new overall status
        self.status_service.update_after_manual_result(result)

        return result
