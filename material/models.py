from django.db import models
from user.models import Classroom


class Material(models.Model):
    type = models.CharField(max_length=50, choices=[
        ('material', 'Material'),
        ('sample', 'Sample'),
    ])
    MATERIAL = 'material'
    SAMPLE = 'sample'
    title = models.CharField(max_length=255)
    content = models.JSONField(null=True, blank=True)

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class FileContent(models.Model):
    file = models.FileField(upload_to='file_contents/')

    def __str__(self):
        return f"{self.file.name} - {self.id}"
    
