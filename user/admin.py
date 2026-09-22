from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Lesson, LessonPackConnector, User, Classroom, MockPackConnector

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Status & Classroom', {'fields': ('status', 'classroom')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'phone_number', 'status', 'classroom', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'username', 'first_name', 'last_name', 'status', 'is_active')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('id',)
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    
admin.site.register(LessonPackConnector)
admin.site.register(Lesson) 
admin.site.register(MockPackConnector)
