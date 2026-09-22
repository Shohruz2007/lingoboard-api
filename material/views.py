from amqp import NotFound
from rest_framework import viewsets, permissions, generics
from rest_framework.parsers import MultiPartParser, FormParser

from .models import FileContent, News, Announcement, Material
from .serializer import FileContentSerializer, NewsSerializer, AnnouncementSerializer, MaterialSerializer


class MaterialModelViewset(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]


class NewsModelViewset(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticated]


class AnnouncementModelViewset(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):

        user = self.request.user
        if user.classroom in [None, []]:
            return Announcement.objects.none()
        return Announcement.objects.filter(classroom__in=user.classroom.all()).distinct()


class FileContentListCreateView(generics.ListCreateAPIView):
    queryset = FileContent.objects.all()
    serializer_class = FileContentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_context(self):
        return {"request": self.request}


class FileContentRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = FileContent.objects.all()
    serializer_class = FileContentSerializer

    def get_object(self):
        lookup_value = self.kwargs.get('lookup_value')

        if lookup_value is None:
            raise NotFound("Lookup value is required")
        if lookup_value.isdigit():
            obj = FileContent.objects.filter(id=int(lookup_value)).first()
            if obj:
                return obj

        obj = FileContent.objects.filter(file__icontains=lookup_value).first()
        if obj:
            return obj

        raise NotFound(f"No file found with id or filename '{lookup_value}'")
    
    def get_serializer_context(self):
        return {"request": self.request}