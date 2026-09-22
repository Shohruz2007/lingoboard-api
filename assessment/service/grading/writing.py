from .base import BaseGrader
from utils.writing_grading_utils import grade_input_text


class WritingGrader(BaseGrader):
    """
    Grader for writing assessments.

    Uses an AI-based grading function to generate feedback and suggestions.
    Score is not computed automatically for writing sections.
    """
    def grade(self, section, user_answers):
        try:
            suggestion = grade_input_text(user_answers)
        except Exception as e:
            # In case the AI grading fails, return no suggestion but log or handle as needed
            suggestion = None

        return {
            'score': None,
            'explanation': {},
            'suggestion': suggestion
        }
