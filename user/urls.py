from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ClassroomModelViewset, LessonModelViewset, LessonRetrieve, RegisterView, UserByAdminView, UserProfileView, LogoutView, CustomLoginView, MockPackConnectorModelViewset

router = DefaultRouter()
router.register(r'classroom', ClassroomModelViewset, basename='classroom')
router.register(r'list', UserByAdminView, basename='user')
router.register(r'lesson/get', LessonRetrieve, basename='lesson')
router.register(r'lesson', LessonModelViewset, basename='lessons')
router.register(r'mock', MockPackConnectorModelViewset, basename='mock')


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomLoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]
