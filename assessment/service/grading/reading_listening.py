from assessment.domain.models import AssessmentSectionAnswer
from utils.grading_utils import merge_answer_list_to_dict, calculate_score
from .base import BaseGrader


class BasicGrader(BaseGrader):
    """
    Grader for reading and listening assessments.

    This fetches the answer key, merges answers into dicts, computes score,
    and returns any explanation embedded in the section's content_data.
    """

    def grade(self, section, user_answers):
        # Retrieve the stored correct answers for this section
        answer_obj = AssessmentSectionAnswer.objects.filter(
            assessment_section=section
        ).first()
        if not answer_obj or answer_obj.answers is None:
            return {"score": None, "explanation": {}, "suggestion": None}

        # Merge lists into dicts for comparison
        print("answer_obj.answers",answer_obj.answers)
        print("user_answers",user_answers)
        correct_answers = merge_answer_list_to_dict(answer_obj.answers)
        submitted = merge_answer_list_to_dict(user_answers)

        # Calculate score
        score = calculate_score(submitted, correct_answers)

        # Extract explanation if available
        explanation = {}
        content_data = getattr(section, "content_data", {})
        if isinstance(content_data, dict):
            explanation = content_data.get("explanation", {})

        return {"score": score, "explanation": explanation, "suggestion": None}
