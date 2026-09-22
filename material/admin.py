from django.contrib import admin
from .models import Material, FileContent, News, Announcement

admin.site.register([
    Material,
    FileContent,
    News,
    Announcement
])
