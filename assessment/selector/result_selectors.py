from typing import Optional
from django.db.models import QuerySet

from assessment.domain.models import AssessmentStudentResult, AssessmentStudentStatus


def get_user_results(user, assessment_id) -> QuerySet[AssessmentStudentResult]:
    """
    Retrieves all AssessmentStudentResult entries for a given user and assessment.
    Returns an empty QuerySet if no status or results exist.
    """
    status = AssessmentStudentStatus.objects.filter(
        user=user,
        assessment_id=assessment_id
    ).first()
    if not status:
        return AssessmentStudentResult.objects.none()

    section_ids = status.completed_sections.values_list('id', flat=True)
    return AssessmentStudentResult.objects.filter(
        user=user,
        assessment_section_id__in=section_ids
    )


def get_result_by_section(user, section_id) -> Optional[AssessmentStudentResult]:
    """
    Retrieves a single AssessmentStudentResult for the given user and section.
    Returns None if no matching result is found.
    """
    return AssessmentStudentResult.objects.filter(
        user=user,
        assessment_section_id=section_id
    ).first()
