from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User


def get_default_created_by_user():
    # Function to get or create a default user
    # This could be a system user or an admin user depending on your application's needs
    user, _ = User.objects.get_or_create(username='default_user', defaults={'email': 'default@example.com'})
    return user.id

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=get_default_created_by_user
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projects', through='Membership')
    deleted_at = models.DateTimeField(null=True)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

class Membership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    can_add_members = models.BooleanField(default=False)
    can_edit_project = models.BooleanField(default=False)
    can_delete_project = models.BooleanField(default=False)

    def set_can_add_members(self, value: bool):
        self.can_add_members = value
        self.save()

    def set_can_edit_project(self, value: bool):
        self.can_edit_project = value
        self.save()

    def set_can_delete_project(self, value: bool):
        self.can_delete_project = value
        self.save()

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50)
    due_date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()
