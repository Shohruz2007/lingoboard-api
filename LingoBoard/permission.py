from rest_framework import permissions
from user.models import User


class TeacherStatusPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.status == User.TEACHER or request.user.is_superuser)

class ReadOnlyOrTeacherPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET' and request.user.is_authenticated:
            return True
        return request.user.is_authenticated and (request.user.status == User.TEACHER or request.user.is_superuser)
