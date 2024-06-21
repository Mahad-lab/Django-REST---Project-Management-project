from rest_framework import viewsets
from rest_framework.response import Response
from .models import Project, Task, Membership
from .serializers import ProjectSerializer, TaskSerializer
from .permissions import IsProjectCreatorOrMemberWithPermission, HasTaskPermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.filter(deleted_at__isnull=True)
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectCreatorOrMemberWithPermission]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Project.objects.filter(deleted_at__isnull=True)
        elif user.is_authenticated:
            return Project.objects.filter(members=user, deleted_at__isnull=True)
        else:
            # Handle unauthenticated access if necessary, or raise an error
            return Project.objects.none()
        # return Project.objects.filter(members=user, deleted_at__isnull=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not Membership.objects.filter(project=instance, member=request.user, can_delete_project=True).exists():
            return Response({"detail": "You do not have permission to delete this project."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.filter(deleted_at__isnull=True)
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, HasTaskPermission]