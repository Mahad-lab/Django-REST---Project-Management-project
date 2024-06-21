from django.urls import reverse
from django.test import TestCase
from base.models import Project, Task, Membership
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.utils import timezone
from django.contrib.auth.models import User

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
        # Authenticate the client
        self.client = APIClient()
        self.user_data = {
            "username": "user1",
            "password": "password123"
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)
        self.token = self.client.post(reverse('token_obtain_pair'), self.user_data, format='json').data['access']
        # self.project = Project.objects.create(name="Sample Project", description="Sample Description")
        self.project = Project.objects.create(name="Sample Project", description="Sample Description", created_by=self.user)
        # self.project.members.add(self.user) 
        # OR
        Membership.objects.create(project=self.project, member=self.user, can_delete_project=True)
        self.project.save()
        self.project_id = self.project.id

    def test_create_project(self):
        """
        Ensure we can create a new project object.
        """
        url = reverse('project-list')  # Adjust 'project-list' to match your actual URL name for project creation
        data = {'name': 'New Project', 'description': 'New Description'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(Project.objects.get(id=2).name, 'New Project')

    def test_get_project_list(self):
        """
        Ensure we can retrieve a list of projects.
        """
        url = reverse('project-list')  # Adjust 'project-list' to match your actual URL name for project list
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming there's only the setUp project in the database

    def test_update_project(self):
        """
        Ensure we can update an existing project.
        """
        url = reverse('project-detail', args=[self.project.id])  
        data = {'name': 'Updated Project', 'description': 'Updated Description'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
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
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
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

    def test_project_permissions(self):
        """
        Ensure only the project creator or a member with permission can delete a project.
        """
        # Create a new user
        user2 = User.objects.create_user(username='user2', password='password123')
        token2 = self.client.post(reverse('token_obtain_pair'), {'username': 'user2', 'password': 'password123'}, format='json').data['access']
        # Create a new project
        project2 = Project.objects.create(name="Project 2", description="Project 2 Description", created_by=user2)
        project2_id = project2.id
        # Authenticate the new user
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token2)
        # Attempt to delete the project created by another user
        url = reverse('project-detail', args=[self.project_id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Attempt to delete the project created by the authenticated user
        url = reverse('project-detail', args=[project2_id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class TaskTestCase(TestCase):
    def test_create_task(self):
        project = Project.objects.create(name="Task Project", description="Task Description")
        task = Task(title="Test Task", description="Test Description", status="To Do", due_date=timezone.now(), project=project)
        task.save()
        self.assertTrue(Task.objects.filter(title="Test Task").exists())

    def test_soft_delete_task(self):
        project = Project.objects.create(name="Task Project", description="Task Description")
        task = Task.objects.create(title="Delete Test", description="Delete Description", status="To Do", due_date=timezone.now(), project=project)
        task_id = task.id
        task.delete()
        deleted_task = Task.objects.get(id=task_id)
        self.assertIsNotNone(deleted_task.deleted_at)

    def test_task_fields(self):
        project = Project.objects.create(name="Task Project", description="Task Description")
        task = Task(title="Field Test", description="Testing Fields", status="To Do", due_date=timezone.now(), project=project, deleted_at=timezone.now())
        task.save()
        saved_task = Task.objects.get(title="Field Test")
        self.assertEqual(saved_task.title, "Field Test")
        self.assertEqual(saved_task.description, "Testing Fields")
        self.assertEqual(saved_task.status, "To Do")
        self.assertIsNotNone(saved_task.deleted_at)
    
# with out authentication
# class TaskAPITests(APITestCase):
#     def setUp(self):
#         # Create a sample project to be used in the tests
#         self.project = Project.objects.create(name="Sample Project", description="Sample Description")
#         # Create a sample task to be used in the tests
#         self.task = Task.objects.create(title="Sample Task", description="Sample Description", status="To Do", due_date=timezone.now(), project=self.project)

#     def test_create_task(self):
#         """
#         Ensure we can create a new task object.
#         """
#         url = reverse('task-list')
#         due_date_formatted = timezone.now().date().isoformat()
#         data = {
#             'title': 'New Task', 
#             'description': 'New Description', 
#             'status': 'To Do', 
#             'due_date': due_date_formatted, 
#             'project': self.project.id
#         }
#         response = self.client.post(url, data, format='json')
#         # print(response.data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Task.objects.count(), 2)
#         self.assertEqual(Task.objects.get(id=2).title, 'New Task')

#     def test_get_task_list(self):
#         """
#         Ensure we can retrieve a list of tasks.
#         """
#         url = reverse('task-list')  # Adjust 'task-list' to match your actual URL name for task list
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)  # Assuming there's only the setUp task in the database

#     def test_update_task(self):
#         """
#         Ensure we can update an existing task.
#         """
#         url = reverse('task-detail', args=[self.task.id])  
#         due_date_formatted = timezone.now().date().isoformat()
#         data = {
#             'title': 'Updated Task', 
#             'description': 'Updated Description', 
#             'status': 'Done', 
#             'due_date': due_date_formatted, 
#             'project': self.project.id
#         }
#         response = self.client.put(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.task.refresh_from_db()
#         self.assertEqual(self.task.title, 'Updated Task')
#         self.assertEqual(self.task.description, 'Updated Description')
#         self.assertEqual(self.task.status, 'Done')

#     def test_soft_delete_task(self):
#         """
#         Ensure we can soft delete a task by setting the deleted_at timestamp.
#         """
#         url = reverse('task-detail', args=[self.task.id])  
#         response = self.client.delete(url, format='json', follow=True)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
#         # Fetch the supposedly deleted task from the database
#         task = Task.objects.get(id=self.task.id)
#         # Check if the task's deleted_at is set, indicating a soft delete
#         self.assertIsNotNone(task.deleted_at)
#         self.assertTrue(isinstance(task.deleted_at, timezone.datetime))
#         # Optionally, ensure the total count of tasks hasn't decreased, indicating the task is not actually removed
#         self.assertEqual(Task.objects.filter(deleted_at__isnull=True).count(), 0)
#         # Optionally, ensure the total count of tasks has decreased, indicating the task is actually removed
#         self.assertEqual(Task.objects.count(), 1)

class TokenObtainPairTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "username": "user1",
            "password": "password123"
        }
        self.url = reverse('token_obtain_pair')
        self.user = User.objects.create_user(**self.user_data)

    def test_obtain_token(self):
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_invalid_username(self):
        invalid_username_data = {
            "username": "wrong",
            "password": self.user_data["password"]
        }
        response = self.client.post(self.url, invalid_username_data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_password(self):
        invalid_password_data = {
            "username": self.user_data["username"],
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, invalid_password_data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_username(self):
        missing_username_data = {
            "password": self.user_data["password"]
        }
        response = self.client.post(self.url, missing_username_data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_password(self):
        missing_password_data = {
            "username": self.user_data["username"]
        }
        response = self.client.post(self.url, missing_password_data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

class UserSignUpTest(APITestCase):
    def test_user_signup(self):
        url = reverse('user_signup')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)