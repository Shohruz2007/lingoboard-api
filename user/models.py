from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from assessment.domain.models import Assessment, MockExam


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class Classroom(models.Model):
    name = models.CharField(max_length=50)
    schedule = models.TimeField(null=True, blank=True)
    classroom_duration = models.PositiveIntegerField(default=60)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = [
        ("starter", "Starter"),
        ("advanced", "Advanced"),
        ("vip", "VIP"),
        ("individual", "Individual"),
        ("teacher", "Teacher"),
    ]
    STARTER = "starter"
    ADVANCED = "advanced"
    VIP = "vip"
    INDIVIDUAL = "individual"
    TEACHER = "teacher"

    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    username = models.CharField(max_length=30, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    classroom = models.ManyToManyField(Classroom, blank=True)
    image = models.ImageField(upload_to="user_images/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["status"]

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["first_name", "last_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class LessonPackConnector(models.Model):
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name="classroom", blank=True
    )
    lesson = models.ManyToManyField("Lesson", related_name="lesson", blank=True)
    current_lesson = models.ForeignKey(
        "Lesson", on_delete=models.CASCADE, null=True, blank=True
    )
    deadline = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    order_number = models.PositiveIntegerField(default=0, unique=True)
    material = models.ManyToManyField(
        "material.Material", related_name="materials", blank=True
    )
    assessment = models.ManyToManyField(
        Assessment, related_name="assessments", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title


class MockPackConnector(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    mock = models.ForeignKey(MockExam, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.classroom.name} - {self.mock.title}"
