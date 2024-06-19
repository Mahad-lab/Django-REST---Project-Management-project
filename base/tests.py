from django.urls import reverse
from django.test import TestCase
from base.models import Project, Task
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

# Create your tests here.

class Test(TestCase):
    def test_1(self):
        self.assertEqual(1, 1)

class ProjectTestCase(TestCase):
    def test_create_project(self):
        project = Project(name="Test Project", description="Test Description")
        project.save()
        self.assertTrue(Project.objects.filter(name="Test Project").exists())

    def test_soft_delete_project(self):
        project = Project.objects.create(name="Delete Test", description="Delete Description")
        project_id = project.id
        project.delete()
        deleted_project = Project.objects.get(id=project_id)
        self.assertIsNotNone(deleted_project.deleted_at)

    def test_project_name_uniqueness(self):
        Project(name="Unique Name", description="Unique Description").save()
        with self.assertRaises(Exception):
            Project(name="Unique Name", description="Another Description").save()

    def test_project_fields(self):
        project = Project(name="Field Test", description="Testing Fields", deleted_at=timezone.now())
        project.save()
        saved_project = Project.objects.get(name="Field Test")
        self.assertEqual(saved_project.name, "Field Test")
        self.assertEqual(saved_project.description, "Testing Fields")
        self.assertIsNotNone(saved_project.deleted_at)

class ProjectAPITests(APITestCase):
    def setUp(self):
        # Create a sample project to be used in the tests
        self.project = Project.objects.create(name="Sample Project", description="Sample Description")

    def test_create_project(self):
        """
        Ensure we can create a new project object.
        """
        url = reverse('project-list')  # Adjust 'project-list' to match your actual URL name for project creation
        data = {'name': 'New Project', 'description': 'New Description'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.get(id=2).name, 'New Project')

    def test_get_project_list(self):
        """
        Ensure we can retrieve a list of projects.
        """
        url = reverse('project-list')  # Adjust 'project-list' to match your actual URL name for project list
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming there's only the setUp project in the database

    def test_update_project(self):
        """
        Ensure we can update an existing project.
        """
        url = reverse('project-detail', args=[self.project.id])  
        data = {'name': 'Updated Project', 'description': 'Updated Description'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project')
        self.assertEqual(self.project.description, 'Updated Description')
        
    def test_soft_delete_project(self):
        """
        Ensure we can soft delete a project by setting the deleted_at timestamp.
        """
        url = reverse('project-detail', args=[self.project.id])  
        response = self.client.delete(url, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Fetch the supposedly deleted project from the database
        project = Project.objects.get(id=self.project.id)
        # Check if the project's deleted_at is set, indicating a soft delete
        self.assertIsNotNone(project.deleted_at)
        self.assertTrue(isinstance(project.deleted_at, timezone.datetime))
        # Optionally, ensure the total count of projects hasn't decreased, indicating the project is not actually removed
        self.assertEqual(Project.objects.filter(deleted_at__isnull=True).count(), 0)
        # Optionally, ensure the total count of projects has decreased, indicating the project is actually removed
        self.assertEqual(Project.objects.count(), 1)
