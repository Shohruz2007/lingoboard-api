from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from user.models import User, Classroom
from assessment.domain.models import Assessment, AssessmentItem, AssessmentResult, AssessmentAnswer, MockExam

class AssessmentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.classroom = Classroom.objects.create(name="IELTS A")

        self.register_url = reverse("register")
        self.login_url = reverse("token_obtain_pair")

        # Register users
        self.student_data = {"username": "student1", "password": "Stud1234!", "status": "starter"}
        self.teacher_data = {"username": "teacher1", "password": "Teach1234!", "status": "teacher"}
        self.client.post(self.register_url, self.student_data)
        self.client.post(self.register_url, self.teacher_data)

        self.student = User.objects.get(username="student1")
        self.teacher = User.objects.get(username="teacher1")
        self.student.classroom = self.classroom
        self.teacher.classroom = self.classroom
        self.student.save()
        self.teacher.save()

        self.student_token = self._get_token(self.student_data)
        self.teacher_token = self._get_token(self.teacher_data)

        # Create assessment
        self.assessment = Assessment.objects.create(
            title="Grammar Test", type="grammar", time_limit_minutes=20, classroom=self.classroom
        )
        self.item1 = AssessmentItem.objects.create(
            assessment=self.assessment,
            question_text="Choose correct form: 'He ___ playing.'",
            correct_answer="is",
            choices={"A": "are", "B": "is", "C": "am"}
        )
        self.item2 = AssessmentItem.objects.create(
            assessment=self.assessment,
            question_text="Synonym of 'quick'?",
            correct_answer="fast"
        )

        # Create mock exam
        self.mock_exam = MockExam.objects.create(
            title="IELTS Mock 1", time_limit_minutes=120, classroom=self.classroom
        )

    def _get_token(self, user_data):
        response = self.client.post(self.login_url, {
            "username": user_data["username"],
            "password": user_data["password"]
        })
        return response.data["access"]

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_student_sees_assessments_for_classroom(self):
        self._auth(self.student_token)
        res = self.client.get("/assessments/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_student_can_see_items_for_assessment(self):
        self._auth(self.student_token)
        res = self.client.get(f"/items/?assessment={self.assessment.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)

    def test_student_can_submit_results(self):
        self._auth(self.student_token)
        payload = {
            "assessment": self.assessment.id,
            "score": 100,
            "answers": [
                {"item": self.item1.id, "user_answer": "is", "is_correct": True},
                {"item": self.item2.id, "user_answer": "fast", "is_correct": True}
            ]
        }
        res = self.client.post("/results/", payload, format="json")
        self.assertEqual(res.status_code, 201)

    def test_student_fetches_own_results(self):
        AssessmentResult.objects.create(assessment=self.assessment, user=self.student, score=90)
        self._auth(self.student_token)
        res = self.client.get("/results/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_teacher_can_see_answers_in_classroom(self):
        result = AssessmentResult.objects.create(assessment=self.assessment, user=self.student, score=80)
        AssessmentAnswer.objects.create(result=result, item=self.item1, user_answer="are", is_correct=False)
        self._auth(self.teacher_token)
        res = self.client.get("/answers/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_student_can_see_mock_exam(self):
        self._auth(self.student_token)
        res = self.client.get("/mocks/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "IELTS Mock 1")

    def test_student_cannot_create_assessment(self):
        self._auth(self.student_token)
        res = self.client.post("/assessments/", {
            "title": "Hacked Test",
            "type": "reading",
            "time_limit_minutes": 15,
            "classroom": self.classroom.id
        })
        self.assertIn(res.status_code, [403, 401])
