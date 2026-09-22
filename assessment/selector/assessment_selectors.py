from django.db.models import QuerySet

from assessment.domain.models import (
    Assessment,
    AssessmentStudentResponse,
    AssessmentSectionAnswer,
    MockExam
)
from user.models import Lesson


def get_assessments_for_lesson(lesson_id: int) -> QuerySet[Assessment]:
    """
    Returns all Assessments associated with the given Lesson.
    """
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Assessment.objects.none()
    # 'assessment' is the related_name on Lesson for Assessments
    return lesson.assessment.all()

def get_assessments_for_mock(mock_id: int) -> QuerySet[Assessment]: 
    """
    Returns all Assessments associated with the given Mock Exam ID.
    """
    try:
        mock_exam = MockExam.objects.get(id=mock_id)
    except MockExam.DoesNotExist:
        return Assessment.objects.none()
    
    return mock_exam.assessments.all()

def has_response(user, section) -> bool:
    """
    Checks if the user has already submitted a response for the given section.
    """
    return AssessmentStudentResponse.objects.filter(
        user=user,
        assessment_section=section
    ).exists()


def get_correct_answers(section_id: int):
    """
    Retrieves the stored correct answers for a section, or None if not set.
    """
    answer = AssessmentSectionAnswer.objects.filter(
        assessment_section_id=section_id
    ).first()
    return answer.answers if answer else None
