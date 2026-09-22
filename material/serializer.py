from rest_framework import serializers
from .models import FileContent, News, Announcement, Material
from user.models import Classroom

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class AnnouncementSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(), many=False
    )
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class MaterialSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Material
        fields = ['id', 'type', 'title', 'content']
        read_only_fields = ['id']
        
class FileContentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = FileContent
        fields = ['id', 'file', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None