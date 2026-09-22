from datetime import timedelta
from pyexpat import model
from django.utils import timezone
from django.db import models
from django.conf import settings

# Using string reference to avoid circular import


class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ("vocabulary", "Vocabulary"),
        ("grammar", "Grammar"),
        ("reading", "Reading"),
        ("listening", "Listening"),
        ("speaking", "Speaking"),
        ("writing", "Writing"),
    ]

    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    READING = "reading"
    LISTENING = "listening"
    SPEAKING = "speaking"
    WRITING = "writing"

    type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.type} - {self.id}"


class AssessmentSection(models.Model):
    title = models.CharField(max_length=255)
    part_name = models.IntegerField()
    assessment = models.ForeignKey(
        Assessment, related_name="content_sections", on_delete=models.CASCADE
    )
    content_data = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=["assessment"]),
            models.Index(fields=["part_name"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.assessment}"


class AssessmentSectionAnswer(models.Model):
    assessment_section = models.ForeignKey(AssessmentSection, on_delete=models.CASCADE)
    answers = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=["assessment_section"]),
        ]

    def __str__(self):
        return f"{self.assessment_section.title} - Answers"


class AssessmentStudentResponse(models.Model):
    assessment_section = models.ForeignKey(AssessmentSection, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answers = models.JSONField()
    stopwatch = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "assessment_section"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]


class AssessmentStudentResult(models.Model):
    assessment_section = models.ForeignKey(AssessmentSection, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.CharField(max_length=50, null=True, blank=True)
    explanation = models.JSONField(null=True, blank=True)
    suggestion = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "assessment_section"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment_section.title} - {self.score}"


class MockExam(models.Model):
    title = models.CharField(max_length=255)
    assessments = models.ManyToManyField(Assessment, blank=True)
    time_limit_minutes = models.PositiveIntegerField()
    start_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def end_time(self):
        if self.start_time:
            return self.start_time + timedelta(minutes=self.time_limit_minutes)
        return None

    def is_active(self):
        now = timezone.now() + timedelta(hours=5)  # Adjust timezone
        return self.start_time and self.start_time <= now <= self.end_time


class AssessmentStudentStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ("not_ready", "Not Ready"),
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("not_graded", "Not Graded"),
            ("graded", "Graded"),
        ],
    )
    NOT_READY = "not_ready"
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    NOT_GRADED = "not_graded"
    GRADED = "graded"
    completed_sections = models.ManyToManyField(
        AssessmentSection, blank=True, related_name="completed_by_users"
    )

    class Meta:
        indexes = [
            models.Index(fields=["user", "assessment"]),
            models.Index(fields=["status"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.assessment} - {self.status}"


class ProgressTrack(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ManyToManyField(Assessment, blank=True)
    lesson_id = models.ForeignKey(
        "user.Lesson", on_delete=models.DO_NOTHING, null=True, blank=True
    )
    mock_id = models.ForeignKey(
        "assessment.MockExam", on_delete=models.DO_NOTHING, null=True, blank=True
    )
    section_list = models.ManyToManyField(AssessmentSection, blank=True)
    result_list = models.ManyToManyField(AssessmentStudentResult, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "lesson_id"]),
            models.Index(fields=["user", "mock_id"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(lesson_id__isnull=False, mock_id__isnull=True)
                    | models.Q(lesson_id__isnull=True, mock_id__isnull=False)
                ),
                name="progress_track_lesson_or_mock",
            )
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if not (self.lesson_id or self.mock_id):
            raise ValidationError("Either lesson_id or mock_id must be provided.")
        if self.lesson_id and self.mock_id:
            raise ValidationError("Cannot have both lesson_id and mock_id.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        context = (
            f"Lesson: {self.lesson_id.title}"
            if self.lesson_id
            else f"Mock: {self.mock_id.title}"
        )
        assessment_names = ", ".join([str(a) for a in self.assessment.all()])
        return f"{self.user.username} - {assessment_names} - {context}"
