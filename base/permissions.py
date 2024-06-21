from rest_framework.permissions import BasePermission, SAFE_METHODS

# class IsProjectMemberOrAdmin(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return request.user in obj.members.all() or obj.created_by == request.user

class IsProjectCreatorOrMemberWithPermission(BasePermission):
    """
    Custom permission to only allow creators of a project or members with permission to delete it.
    """

    def has_object_permission(self, request, view, obj):
        # If so, permission is granted
        if request.method in SAFE_METHODS:
            return True

        # Check if the user is the creator of the project
        if obj.created_by == request.user:
            return True

        # Check if the user is a member with delete permission
        return obj.members.filter(user=request.user, can_delete_project=True).exists()

class HasTaskPermission(BasePermission):
    """
    Custom permission to only allow users with a specific task permission.
    """

    def has_permission(self, request, view):
        # Implement general task-based permission logic here
        # For example, check if the user has a specific role or permission
        return request.user.has_perm('app_label.task_permission')

    def has_object_permission(self, request, view, obj):
        # Implement object-specific task-based permission logic here
        # For example, check if the user is the owner of the object
        return obj.project.created_by == request.user or obj.project.members.filter(user=request.user, can_edit_project=True).exists()