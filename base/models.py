from django.db import models
from django.utils import timezone

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    deleted_at = models.DateTimeField(null=True)

    def delete(self):
        self.deleted_at = timezone.now()
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
