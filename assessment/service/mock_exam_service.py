from rest_framework.exceptions import NotFound, PermissionDenied
from django.utils import timezone

from assessment.domain.models import MockExam, AssessmentStudentStatus, AssessmentStudentResult
from assessment.serializer.result_serializers import AssessmentStudentResultSerializer


class MockExamService:
    """
    Service to handle mock exam access, start, and force-close operations.
    """
    def get_mock_exams_all(self):
        """
        Fetch all active mock exams.
        """
        return MockExam.objects.all()
    
    def get_mock_exam(self, mock_exam_id):
        """
        Fetch a MockExam instance by ID.
        """
        try:
            return MockExam.objects.get(id=mock_exam_id)
        except MockExam.DoesNotExist: 
            raise NotFound("Mock exam not found.")
    
    def access_exam(self, user, mock_exam_id):
        # Fetch the MockExam instance
        mock_exam = self.get_mock_exam(mock_exam_id)

        # Check if the exam is currently active
        if not mock_exam.is_active():
            raise PermissionDenied("Exam is not currently active.")

        assessments = mock_exam.assessments.all()
        accessible = []
        all_graded = True

        # Ensure statuses exist and collect accessible assessments
        for assessment in assessments:
            status_obj, created = AssessmentStudentStatus.objects.get_or_create(
                user=user,
                assessment=assessment,
                defaults={"status": AssessmentStudentStatus.NOT_STARTED}
            )

            if status_obj.status == AssessmentStudentStatus.NOT_STARTED:
                status_obj.status = AssessmentStudentStatus.IN_PROGRESS
                status_obj.save()
                accessible.append(assessment.id)

            if status_obj.status != AssessmentStudentStatus.GRADED:
                all_graded = False

        # If everything graded, return all results
        if all_graded:
            results = AssessmentStudentResult.objects.filter(
                user=user,
                assessment_section__assessment__in=assessments
            )
            data = AssessmentStudentResultSerializer(results, many=True).data
            return {
                "status": AssessmentStudentStatus.GRADED,
                "results": data
            }

        # If none started, forbid access
        if not accessible:
            raise PermissionDenied("No assessments available to start.")

        # Otherwise return in-progress payload
        return {
            "status": AssessmentStudentStatus.IN_PROGRESS,
            "accessible_assessments": accessible
        }

    def start_now(self, mock_exam_id):
        # Immediately start the exam by setting start_time to now
        try:
            mock_exam = MockExam.objects.get(id=mock_exam_id)
        except MockExam.DoesNotExist:
            raise NotFound("Mock exam not found.")

        mock_exam.start_time = timezone.now()
        mock_exam.save()
        return {"message": "Mock exam started now."}

    def force_close(self, mock_exam_id):
        # Force-close the exam by marking remaining statuses NOT_GRADED
        try:
            mock_exam = MockExam.objects.get(id=mock_exam_id)
        except MockExam.DoesNotExist:
            raise NotFound("Mock exam not found.")

        assessments = mock_exam.assessments.all()
        statuses = AssessmentStudentStatus.objects.filter(
            assessment__in=assessments,
            status__in=[
                AssessmentStudentStatus.NOT_STARTED,
                AssessmentStudentStatus.IN_PROGRESS,
                AssessmentStudentStatus.NOT_GRADED
            ]
        )
        statuses.update(status=AssessmentStudentStatus.NOT_GRADED)
        return {"message": "Mock exam forcibly closed. All unfinished statuses set to NOT_GRADED."}
