from django.urls import path, include
from rest_framework.routers import DefaultRouter
from base.views import ProjectViewSet, TaskViewSet, UserSignUpView

# router for ViewSets.
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', UserSignUpView.as_view(), name='user_signup'),
]