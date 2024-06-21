from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Project, Task, Membership
from .serializers import ProjectSerializer, TaskSerializer, UserRegistrationSerializer
from .permissions import IsProjectCreatorOrMemberWithPermission, HasTaskPermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action


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


class UserSignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserRegistrationSerializer(user).data,
                "message": "User created successfully."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@action(detail=True, methods=['post'], permission_classes=[IsProjectCreatorOrMemberWithPermission])
def set_member_permission(self, request, pk=None):
    project = self.get_object()
    user_id = request.data.get('user_id')
    permission_type = request.data.get('permission_type')  # e.g., 'can_edit_project'
    permission_value = request.data.get('permission_value', True)

    try:
        membership = Membership.objects.get(project=project, member_id=user_id)
        if permission_type == 'can_edit_project':
            membership.set_can_edit_project(permission_value)
        elif permission_type == 'can_delete_project':
            membership.set_can_delete_project(permission_value)
        elif permission_type == 'can_add_members':
            membership.set_can_add_members(permission_value)
        else:
            return Response({"detail": "Invalid permission type."}, status=400)

        return Response({"detail": "Permission updated successfully."})
    except Membership.DoesNotExist:
        return Response({"detail": "Membership not found."}, status=404)