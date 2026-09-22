from assessment.domain.models import (
    AssessmentStudentResult,
    AssessmentStudentStatus,
    AssessmentSection,
)


class StatusService:
    """
    Manages AssessmentStudentStatus transitions after submissions and manual result updates.
    """

    def update_after_submission(self, user, assessment, completed_section):
        # Get or create status
        status_obj, _ = AssessmentStudentStatus.objects.get_or_create(
            user=user,
            assessment=assessment,
            defaults={"status": AssessmentStudentStatus.IN_PROGRESS},
        )
        # Mark the new section as completed
        status_obj.completed_sections.add(completed_section)

        # Gather all sections for this assessment
        section_ids = AssessmentSection.objects.filter(
            assessment=assessment
        ).values_list("id", flat=True)

        # Fetch all results for the user on these sections
        results = AssessmentStudentResult.objects.filter(
            user=user, assessment_section_id__in=section_ids
        ).select_related("assessment_section")

        # Determine new status
        if results.count() == len(section_ids):
            scores = [r.score for r in results]
            if all(score and score != "0/0" for score in scores):
                new_status = AssessmentStudentStatus.GRADED
            elif any(score is not None for score in scores):
                new_status = AssessmentStudentStatus.NOT_GRADED
            else:
                new_status = AssessmentStudentStatus.IN_PROGRESS
        else:
            new_status = AssessmentStudentStatus.IN_PROGRESS

        # Save status
        status_obj.status = new_status
        status_obj.save()

    def update_after_manual_result(self, result_obj):
        """
        Should be called when an instructor manually updates an AssessmentStudentResult.
        Recomputes the overall status for the user and assessment.
        """
        user = result_obj.user
        assessment = result_obj.assessment_section.assessment

        # Delegate to same logic by faking a completed_section
        # but ensure status object exists
        status_obj, _ = AssessmentStudentStatus.objects.get_or_create(
            user=user,
            assessment=assessment,
            defaults={"status": AssessmentStudentStatus.IN_PROGRESS},
        )
        # Recompute exactly as after submission
        # (no need to modify completed_sections here)
        section_ids = AssessmentSection.objects.filter(
            assessment=assessment
        ).values_list("id", flat=True)
        results = AssessmentStudentResult.objects.filter(
            user=user, assessment_section_id__in=section_ids
        )

        if results.count() == len(section_ids):
            scores = [r.score for r in results]
            if all(score and score != "0/0" for score in scores):
                new_status = AssessmentStudentStatus.GRADED
            elif any(score is not None for score in scores):
                new_status = AssessmentStudentStatus.NOT_GRADED
            else:
                new_status = AssessmentStudentStatus.IN_PROGRESS
        else:
            new_status = AssessmentStudentStatus.IN_PROGRESS

        status_obj.status = new_status
        status_obj.save()
