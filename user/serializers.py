from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Lesson, LessonPackConnector, MockPackConnector, User, Classroom
from django.contrib.auth.password_validation import validate_password

class ClassroomBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classroom
        fields = ['id', 'name', 'schedule', 'classroom_duration']  # include 'users' field

class ClassroomExtendedSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = ['id', 'name', 'schedule', 'classroom_duration', 'users']  # include 'users' field

    def get_users(self, obj):
        return UserProfileSerializer(obj.user_set.all(), many=True).data

class UserProfileSerializer(serializers.ModelSerializer):
    classroom = ClassroomBaseSerializer(read_only=True, many=True)
    

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'phone_number',
            'username', 'status', 'classroom', 'classroom'
        ]
        read_only_fields = ['id', 'username', 'status', 'classroom_id', 'classroom']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class UserControlSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'username', 'status', 'classroom']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'password', 'status']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['status'] = user.status
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        data['status'] = self.user.status
        return data
    
class LessonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order_number', 'material', 'assessment']
        read_only_fields = ['id']
        
class LessonPackSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = LessonPackConnector
        fields = ['id', 'name', 'lessons']
        read_only_fields = ['id']
        
class MockPackConnectorModelSerializer(serializers.ModelSerializer):
    mock_title = serializers.CharField(source='mock.title', read_only=True)

    class Meta:
        model = MockPackConnector
        fields = ['id', 'classroom', 'mock', 'created_at', 'mock_title']
        read_only_fields = ['id']