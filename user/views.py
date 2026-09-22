from django.forms import ValidationError
from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters

from django.db import models

from django_filters.rest_framework import DjangoFilterBackend

from LingoBoard.permission import *
from user.filters import UserFilter
from .models import Classroom, Lesson, LessonPackConnector, User, MockPackConnector
from .serializers import ClassroomBaseSerializer, ClassroomExtendedSerializer, CustomTokenObtainPairSerializer, LessonPackSerializer, LessonSerializer, RegisterSerializer, UserProfileSerializer, UserControlSerializer, MockPackConnectorModelSerializer


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [TeacherStatusPermission]


class UserProfileView(generics.RetrieveUpdateAPIView):
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PUT'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class UserByAdminView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserControlSerializer
    permission_classes = [TeacherStatusPermission]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['first_name', 'last_name', 'username', 'phone_number']
    ordering_fields = ['created_at', 'updated_at', 'first_name', 'last_name', 'username']
    
    def update(self, request, *args, **kwargs):
        partial = request.method == 'PUT'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"detail": "Logged out successfully."})


class ClassroomModelViewset(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    permission_classes = [TeacherStatusPermission]
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'update':
            return ClassroomExtendedSerializer
        return ClassroomBaseSerializer
    
    def create(self, request, *args, **kwargs):

        new_classroom = Classroom.objects.create(**request.data)
        lessons = Lesson.objects.all().order_by('order_number')
        lessons_ids = lessons.values_list('id', flat=True)
        new_connector = LessonPackConnector.objects.create(classroom=new_classroom)
        new_connector.lesson.set(lessons_ids)
        new_connector.current_lesson = lessons.first() if lessons else None
        new_connector.save()
        return Response({
            "message": "Classroom created successfully",
            "classroom_id": new_classroom.id
        }, status=201)
    
    def update(self, request, *args, **kwargs):
        partial = request.method == 'PUT'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class LessonRetrieve(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        return super().get_queryset().order_by('order_number')



class LessonModelViewset(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [TeacherStatusPermission]

    def get_queryset(self):
        return self.queryset.order_by('order_number')

    def create(self, request, *args, **kwargs):
        order_number = request.data.get('order_number')
        if not order_number or order_number in (None, 0):
            max_order = Lesson.objects.aggregate(max=models.Max('order_number'))['max'] or 0
            request.data['order_number'] = max_order + 1
        
        return super().create(request)

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PUT'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class MockPackConnectorModelViewset(viewsets.ModelViewSet):
    queryset = MockPackConnector.objects.all()
    serializer_class = MockPackConnectorModelSerializer
    permission_classes = [ReadOnlyOrTeacherPermission]
    
    def perform_create(self, serializer):
        classroom = self.request.data.get('classroom')
        mock = self.request.data.get('mock')
        if MockPackConnector.objects.filter(classroom=classroom, mock=mock).exists():
            raise ValidationError("MockPackConnector with this classroom and mock already exists.")
        return super().perform_create(serializer)

    
    def update(self, request, *args, **kwargs):
        classroom = self.request.data.get('classroom')
        mock = self.request.data.get('mock')
        if MockPackConnector.objects.filter(classroom=classroom, mock=mock).exists():
            raise ValidationError("MockPackConnector with this classroom and mock already exists.")
        
        partial = request.method == 'PUT'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)