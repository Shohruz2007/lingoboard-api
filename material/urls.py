from django.urls import path, include
from rest_framework import routers
from .views import FileContentListCreateView, FileContentRetrieveDestroyView, NewsModelViewset, AnnouncementModelViewset, MaterialModelViewset

router = routers.DefaultRouter()
router.register(r'material', MaterialModelViewset, basename='material')
router.register(r'news', NewsModelViewset, basename='news')
router.register(r'announcement', AnnouncementModelViewset, basename='announcement')

urlpatterns = [
    path('', include(router.urls)),
    path('files/', FileContentListCreateView.as_view(), name='file-list-create'),
    path('files/<str:lookup_value>/', FileContentRetrieveDestroyView.as_view(), name='file-retrieve-destroy'),
]