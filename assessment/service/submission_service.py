from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound

from assessment.domain.models import (
    AssessmentSection,
    AssessmentStudentResponse,
    AssessmentStudentResult,
)
from assessment.selector.assessment_selectors import has_response
from assessment.service.grading.registry import GraderRegistry
from assessment.service.status_service import StatusService


class SubmissionService:
    """
    Handles the full workflow of submitting a section: validating, persisting the response,
    performing grading, saving results, and updating student status.
    """
    def __init__(self):
        self.grader_registry = GraderRegistry()
        self.status_service = StatusService()

    @transaction.atomic
    def submit_section(self, user, section: AssessmentSection, answers):


        # 2. Persist student response
        response = AssessmentStudentResponse.objects.create(
            user=user,
            assessment_section=section,
            answers=answers
        )

        # 3. Grade the submission
        grader = self.grader_registry.for_assessment_type(section.assessment.type)
        result_payload = grader.grade(section, answers)

        # 4. Save or update result
        AssessmentStudentResult.objects.update_or_create(
            user=user,
            assessment_section=section,
            defaults=result_payload
        )

        try:
            from utils.cache_manager import fallback_cache
            user_id = user.id if hasattr(user, "id") else str(user)
            cache_keys_to_clear = [
                f"student_results_list_fallback_{user_id}",
                f"student_results_queryset_{user_id}",
            ]
            for key in cache_keys_to_clear:
                fallback_cache.delete(key)
        except Exception as e:
            pass
        
        # 5. Update overall assessment status
        self.status_service.update_after_submission(
            user=user,
            assessment=section.assessment,
            completed_section=section
        )

        return response
