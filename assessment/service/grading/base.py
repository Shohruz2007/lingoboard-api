from abc import ABC, abstractmethod

class BaseGrader(ABC):
    """
    Abstract base grader. Subclasses should implement the grade() method to return a dict with:
      - score: computed score or None
      - explanation: dict or relevant explanation data
      - suggestion: optional suggestion or None
    """

    @abstractmethod
    def grade(self, section, user_answers):
        """
        Grade a given assessment section based on user answers.

        Args:
            section (AssessmentSection): the section to grade
            user_answers (dict or list): the student's submitted answers

        Returns:
            dict: {
              'score': str or None,
              'explanation': dict,
              'suggestion': dict or None
            }
        """
        pass
