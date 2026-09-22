from django.db import transaction
from assessment.domain.models import (
    ProgressTrack,
    AssessmentStudentResult,
    Assessment,
    AssessmentSection,
    MockExam,
)
from user.models import Lesson


class ProgressTrackService:
    """
    Service to manage ProgressTrack creation and updates.
    """

    def update_progress_track(
        self, user, assessment, section, lesson_id=None, mock_id=None
    ):
        """
        Create or update ProgressTrack based on the submission.

        Args:
            user: The user making the submission
            assessment: The assessment being worked on
            section: The section that was submitted
            lesson_id: Optional lesson object for lesson-based progress
            mock_id: Optional mock exam object for mock-based progress
        """
        with transaction.atomic():
            # Get or create ProgressTrack
            progress_track, created = ProgressTrack.objects.get_or_create(
                user=user, lesson_id=lesson_id, mock_id=mock_id, defaults={}
            )

            if created:
                # If this is a new ProgressTrack, populate it with all related data
                self._populate_new_progress_track(
                    progress_track, user, lesson_id, mock_id
                )
            else:
                # If existing ProgressTrack, just add the current assessment and section
                if assessment not in progress_track.assessment.all():
                    progress_track.assessment.add(assessment)

                if section not in progress_track.section_list.all():
                    progress_track.section_list.add(section)

            # Check if there's a result for this section and add it to result_list
            try:
                result = AssessmentStudentResult.objects.get(
                    user=user, assessment_section=section
                )
                if result not in progress_track.result_list.all():
                    progress_track.result_list.add(result)
            except AssessmentStudentResult.DoesNotExist:
                # No result yet, that's fine - it will be added later when grading is complete
                pass

            progress_track.save()
            return progress_track

    def _populate_new_progress_track(
        self, progress_track, user, lesson_id=None, mock_id=None
    ):
        """
        Populate a newly created ProgressTrack with all related assessments, sections, and results.

        Args:
            progress_track: The newly created ProgressTrack instance
            user: The user
            lesson_id: Optional lesson object for lesson-based progress
            mock_id: Optional mock exam object for mock-based progress
        """
        assessments = []
        sections = []

        if lesson_id:
            # lesson_id is now the lesson object itself
            assessments = list(lesson_id.assessment.all())

        elif mock_id:
            # mock_id is now the mock exam object itself
            assessments = list(mock_id.assessments.all())

        # Add all assessments to the progress track
        if assessments:
            progress_track.assessment.set(assessments)

            # Get all sections from all assessments
            for assessment in assessments:
                assessment_sections = AssessmentSection.objects.filter(
                    assessment=assessment
                )
                sections.extend(assessment_sections)

            # Add all sections to the progress track
            if sections:
                progress_track.section_list.set(sections)

                # Get all existing results for this user on these sections
                existing_results = AssessmentStudentResult.objects.filter(
                    user=user, assessment_section__in=sections
                )

                # Add all existing results to the progress track
                if existing_results.exists():
                    progress_track.result_list.set(existing_results)
