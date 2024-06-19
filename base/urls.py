from django.urls import path, include
from rest_framework.routers import DefaultRouter
from base.views import ProjectViewSet, TaskViewSet

# router for ViewSets.
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]