from assessment.domain.models import Assessment
from .base import BaseGrader
from .reading_listening import BasicGrader
from .writing import WritingGrader


class DefaultGrader(BaseGrader):
    """
    Fallback grader when no specific grader is defined for a type.
    """

    def grade(self, section, user_answers):
        return {"score": None, "explanation": {}, "suggestion": None}


class GraderRegistry:
    """
    Registry for mapping assessment types to their respective graders.
    """

    def __init__(self):
        self._map = {
            Assessment.READING: BasicGrader(),
            Assessment.LISTENING: BasicGrader(),
            Assessment.WRITING: WritingGrader(),
            Assessment.VOCABULARY: BasicGrader(),
            Assessment.GRAMMAR: BasicGrader(),
        }
        self._default = DefaultGrader()

    def for_assessment_type(self, assessment_type: str) -> BaseGrader:
        """
        Returns the grader for the given assessment type, or a default grader.
        """
        return self._map.get(assessment_type, self._default)
