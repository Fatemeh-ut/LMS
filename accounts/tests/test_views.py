from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import Users
from rest_framework.test import APIClient

from library import models

User = get_user_model()

class UserRegisterTest(APITestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_register_user_success(self):
        user_data = {
            'username':'usertest',
            'password':'passwordtest!0',
            'password2':'passwordtest!0',
            'email':'user@test.com',
            'first_name':'Test',
            'last_name':'User'
        }
        response = self.client.post(self.url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(Users.objects.filter(username='usertest').exists())

        user_response = response.data['user']
        self.assertEqual(user_response['username'], user_data['username'])
        self.assertEqual(user_response['email'], user_data['email'])

    def test_user_invalid_data(self):
        invalid_user_data = {
            'username':'',
            'password':'ss',
            'password2':'aa',
            'email':'no-email'
        }
        response = self.client.post(self.url, invalid_user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Users.objects.filter(email='no-email').exists())


class UserLoginTest(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = Users.objects.create_user(
            username='test_user',
            password='password!0',
            email='user@test.com',
            first_name='user',
            last_name='test'
        )
    def test_login_success(self):
        user_login_data = {
            'username':'test_user',
            'password':'password!0'
        }
        response = self.client.post(self.url, user_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        try:
            refresh = RefreshToken(response.data['refresh'])
            access = AccessToken(response.data['access'])
            self.assertTrue(refresh)
            self.assertTrue(access)
        except Exception as e:
            self.fail(f'faild to create token {e}')
    def test_login_invalid_data(self):
        invalid_data = {
            'username':'dd',
            'password':'password!0'
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_no_username(self):
        data = {
            'password':'password!0'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_no_password(self):
        data = {
          'username': 'test_user'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            role='borrower'
        )
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            password='adminpassword',
            role='admin'
        )
        self.client.login(username='adminuser', password='adminpassword')

        self.list_url = reverse('admin-list')  # مسیر ویو مورد نظر
        self.detail_url = reverse('admin-detail', kwargs={'pk':self.admin_user.pk})

        self.new_user_data = {
            'username': 'new_user',
            'password':'new_password',
            'email':'email@test.com',
            'first_name': 'user',
            'last_name': 'test',
            'role':'borrower'
        }
        self.new_admin_data = {
            'username': 'new_admin',
            'password':'new_password',
            'email':'emailadmin@test.com',
            'first_name':'admin',
            'last_name':'test',
            'role':'admin'
        }


    def test_user_access(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_access(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_admin(self):
        response = self.client.post(self.list_url, self.new_admin_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_admin = User.objects.get(username='new_admin')
        self.assertIsNotNone(new_admin)
        self.assertEqual(new_admin.role, 'admin')

    def test_create_user(self):
        response = self.client.post(self.list_url, self.new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.get(username='new_user')
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.role, 'borrower')

    def test_update_user(self):
        update_data = {
            'email':'update.email@test.com'
        }
        response = self.client.patch(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.email, 'update.email@test.com')

    def test_delete_user(self):
        delete_url = reverse('admin-detail', kwargs={'pk': self.user.pk})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
