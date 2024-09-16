from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import Users
from rest_framework.test import APIClient

from library import models, serializers

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

        self.list_url = reverse('admin-list')
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


class AdminTransactionTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            password='adminpassword',
            role='admin'
        )
        self.user = User.objects.create_user(
            username='username',
            password='userpassword',
            role='borrower'
        )
        self.author = models.Author.objects.create(
            first_name='author',
            last_name = 'test'
        )
        self.book1 = models.Book.objects.create(
            title='book 1',
            author=self.author,
            num_exist=2
        )
        self.book2 = models.Book.objects.create(
            title = 'book 2',
            author = self.author,
            num_exist = 0
        )
        self.transaction1 = models.LendingTransaction.objects.create(
            book=self.book1, borrower=self.user, status='borrowed'
        )
        self.transaction2 = models.LendingTransaction.objects.create(
            book=self.book2, borrower=self.user, status='returned'
        )
        self.list_url = reverse('admin-transaction')


    def test_admin_access_transaction(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

    def test_user_not_access_transaction(self):
        self.client.login(username='username', password='userpassword')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserProfileTest(TestCase):

    def setUp(self):
        self.client=APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin_pass',
            email='admin@test.com',
            first_name='Admin',
            last_name='Test',
            role='admin'
        )
        self.user = User.objects.create_user(
            username='user',
            password='user_password',
            email='user@test.com',
            first_name='User',
            last_name='Test',
            role='borrower'
        )
        self.url = reverse('profile')
    def test_borrower_not_access_profile(self):
        self.client.login(username='user', password='user_name')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_borrower_access_profile(self):
        self.client.login(username='user', password='user_password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertEqual(response.data['email'], self.user.email)


    def test_admin_access_profile(self):
        self.client.login(username='admin', password='admin_pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.admin.first_name)
        self.assertEqual(response.data['last_name'], self.admin.last_name)
        self.assertEqual(response.data['email'], self.admin.email)


class BorrowerTransactionTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.borrower_user = User.objects.create_user(
            username='borrower',
            password='password',
            first_name='Borrower',
            last_name='Test',
            role='borrower'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='password',
            first_name='Admin',
            last_name='Test',
            role='admin'
        )
        self.author = models.Author.objects.create(
            first_name='Author', last_name='Test'
        )
        self.book = models.Book.objects.create(
            title='book', author=self.author, num_exist= 2
        )
        self.transaction1 = models.LendingTransaction.objects.create(
            book=self.book, borrower=self.borrower_user, status='borrowed', borrowed_at='2023-09-10'
        )
        self.transaction2 = models.LendingTransaction.objects.create(
            book=self.book, borrower=self.borrower_user, status='borrowed', borrowed_at='2023-09-12'
        )
        self.transaction_admin = models.LendingTransaction.objects.create(
            book=self.book, borrower=self.admin, status='borrowed', borrowed_at='2023-09-15'
        )
        self.url = reverse('transaction')

    def test_borrower_access_transaction(self):
        self.client.login(username='borrower', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

        serializer = serializers.LendingTransactionUpdate(self.transaction1)
        self.assertIn(serializer.data, response.data)

    def test_admin_not_access_transaction(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(response.data), 0)


class BorrowerNotificationTest(TestCase):
    pass