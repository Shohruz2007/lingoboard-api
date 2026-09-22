from rest_framework.exceptions import NotFound

from assessment.domain.models import (
    AssessmentSection,
    AssessmentStudentStatus,
    AssessmentStudentResult,
)
from assessment.serializer.section_serializers import AssessmentSectionSerializer
from assessment.serializer.result_serializers import AssessmentStudentResultSerializer


class AssessmentAccessService:
    """
    Service to fetch sections for an assessment along with the student's current status,
    completed sections, and any existing results.
    """

    def get_sections_payload(self, assessment_id, user):
        # 1. Get or initialize the student's status for this assessment
        status_obj = (
            AssessmentStudentStatus.objects.filter(
                assessment_id=assessment_id, user=user
            )
            .select_related("assessment")
            .prefetch_related("completed_sections")
            .first()
        )
        if not status_obj:
            status_obj = AssessmentStudentStatus.objects.create(
                assessment_id=assessment_id,
                user=user,
                status=AssessmentStudentStatus.NOT_STARTED,
            )

        # 2. Serialize all sections under this assessment
        sections_qs = AssessmentSection.objects.filter(
            assessment_id=assessment_id
        ).select_related("assessment")
        sections_data = AssessmentSectionSerializer(sections_qs, many=True).data

        # 3. Branch based on status
        status = status_obj.status
        if status == AssessmentStudentStatus.NOT_STARTED:
            return {"status": status, "sections": sections_data}

        if status == AssessmentStudentStatus.IN_PROGRESS:
            completed_ids = list(
                status_obj.completed_sections.values_list("id", flat=True)
            )
            results_qs = AssessmentStudentResult.objects.filter(
                user=user, assessment_section_id__in=completed_ids
            )
            results_data = AssessmentStudentResultSerializer(results_qs, many=True).data
            return {
                "status": status,
                "completed_sections": completed_ids,
                "sections": sections_data,
                "results": results_data,
            }

        if status == AssessmentStudentStatus.NOT_GRADED:
            return {"status": status, "sections": sections_data}

        if status == AssessmentStudentStatus.GRADED:
            results_qs = AssessmentStudentResult.objects.filter(
                user=user, assessment_section__assessment_id=assessment_id
            )
            results_data = AssessmentStudentResultSerializer(results_qs, many=True).data
            return {
                "status": status,
                "results": results_data,
                "sections": sections_data,
            }

        # Unknown status
        raise NotFound("Unknown assessment status for user.")
