from django.test import TestCase
from django.contrib.auth.models import User
from .models import Todo
from django.urls import reverse

class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@example.com', email='testuser@example.com', password='password123'
        )
        self.todo = Todo.objects.create(
            user=self.user,
            title='Buy Milk',
            description='Go to the supermarket',
            priority=Todo.Priority.MEDIUM,
            status=Todo.Status.PENDING
        )

    def test_todo_creation(self):
        self.assertEqual(self.todo.title, 'Buy Milk')
        self.assertEqual(self.todo.status, Todo.Status.PENDING)
        self.assertEqual(self.todo.priority, Todo.Priority.MEDIUM)
        self.assertFalse(self.todo.removed)

class ViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@example.com', email='testuser@example.com', password='password123'
        )
        self.todo = Todo.objects.create(
            user=self.user,
            title='Test Task'
        )

    def test_home_view_requires_login(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/login/?next=/')

    def test_home_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_toggle_todo(self):
        self.client.force_login(self.user)
        self.assertEqual(self.todo.status, Todo.Status.PENDING)

        response = self.client.post(reverse('toggle_todo', args=[self.todo.id]))
        self.assertRedirects(response, reverse('home'))

        self.todo.refresh_from_db()
        self.assertEqual(self.todo.status, Todo.Status.DONE)

    def test_delete_todo(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_todo', args=[self.todo.id]))
        self.assertRedirects(response, reverse('home'))

        self.todo.refresh_from_db()
        self.assertTrue(self.todo.removed)


from rest_framework.test import APITestCase
from rest_framework import status

class TodoAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser@example.com', email='apiuser@example.com', password='apipassword'
        )
        self.other_user = User.objects.create_user(
            username='otheruser@example.com', email='otheruser@example.com', password='otherpassword'
        )
        self.todo = Todo.objects.create(
            user=self.user,
            title='API Task',
            description='Test description'
        )
        self.other_todo = Todo.objects.create(
            user=self.other_user,
            title='Other User Task'
        )

    def test_list_todos_unauthenticated(self):
        response = self.client.get('/api/todos/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_todos_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/todos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that we only list active, un-removed todos for the logged-in user
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'API Task')

    def test_create_todo_api(self):
        self.client.force_login(self.user)
        data = {'title': 'New API Todo', 'priority': 'HIGH'}
        response = self.client.post('/api/todos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Todo.objects.filter(user=self.user, title='New API Todo').count(), 1)

    def test_retrieve_todo_api(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/api/todos/{self.todo.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Task')

    def test_retrieve_other_user_todo_fails(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/api/todos/{self.other_todo.id}/')
        # Should return 404 since queryset is filtered by user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_todo_api(self):
        self.client.force_login(self.user)
        response = self.client.delete(f'/api/todos/{self.todo.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Todo.objects.filter(id=self.todo.id).count(), 0)

    def test_update_todo_api(self):
        self.client.force_login(self.user)
        data = {'title': 'Updated API Task Title'}
        response = self.client.patch(f'/api/todos/{self.todo.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated API Task Title')

    def test_update_other_user_todo_fails(self):
        self.client.force_login(self.user)
        data = {'title': 'Hacked Title'}
        response = self.client.patch(f'/api/todos/{self.other_todo.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_other_user_todo_fails(self):
        self.client.force_login(self.user)
        response = self.client.delete(f'/api/todos/{self.other_todo.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_todo_invalid_title(self):
        self.client.force_login(self.user)
        data = {'title': 'ab'}  # Too short, validation requires at least 3 chars
        response = self.client.post('/api/todos/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)


class UserAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser@example.com', email='apiuser@example.com', password='apipassword'
        )

    def test_list_users_unauthenticated(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
