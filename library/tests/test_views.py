from django.test import TestCase
from datetime import date
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from accounts.models import Users
from library import models

User = get_user_model()

class AuthorViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.user = User.objects.create_user(
            username='user',
            password='user123',
            role='borrower'
        )
        self.author= models.Author.objects.create(
            first_name='author',
            last_name='test',
            birth_date='1990-05-12'
        )
        self.new_author = {
            'first_name':'new author',
            'last_name':'test',
            'birth_date' : '1990-05-12'
        }
        self.list_url = reverse('author-list')
        self.detail_url = reverse('author-detail', kwargs={'pk':self.admin.pk})
    def test_admin_access(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)

    def test_user_not_access(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_author(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(self.list_url, self.new_author, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        author = models.Author.objects.get(id=2)
        self.assertIsNotNone(author)
        self.assertEqual(author.first_name, 'new author')
        self.assertEqual(author.last_name, 'test')


    def test_update_author(self):
        update_data={
            'first_name': 'updated author',  # Include required fields
            'last_name': 'test',
            'birth_date': '1990-05-12'
        }
        self.client.login(username='admin', password='admin123')
        response = self.client.patch(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_author(self):
        self.client.login(username='admin', password='admin123')
        delete_url = reverse('author-detail', kwargs={'pk':self.author.pk})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
"""
class BookViewSetTest(TestCase):
    def setUp(self):
        pass

    def test_create_book(self):
        pass
    

    def test_update_book(self):
        pass

    def test_delete_book(self):
        pass

class CategoryViewSetTest(TestCase):
    def setUp(self):
        pass
    def test_admin_access(self):
        pass
    def test_create_category(self):
        pass
    def test_update_category(self):
        pass
    def test_delete_category(self):
        pass

class AddCommentTest(TestCase):
    def setUp(self):
        pass
    def test_user_access(self):
        pass
    def test_user_add_comment(self):
        pass

class AddTransactionTest(TestCase):
    def setUp(self):
        pass
    def test_borrower_access(self):
        pass
    def test_borrower_add_transaction(self):
        pass
"""