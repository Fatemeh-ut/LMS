from django.contrib.admin.templatetags.admin_list import admin_actions
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from library import models

User = get_user_model()

class AddLoinPeriodTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin', password='admin!0', email='admin@test.com', role='admin'
        )
        self.borrower = User.objects.create_user(
            username='borrower', password='borrower!0', email='borrower@test.com', role='borrower'
        )
        self.author = models.Author.objects.create(
            first_name='author', last_name='test'
        )
        self.book1 = models.Book.objects.create(
            title='book 1', loan_period=0, num_exist=1,author=self.author
        )
        self.book2 = models.Book.objects.create(
            title='book 2', loan_period=5, num_exist=1,author=self.author
        )
        self.url = reverse('loan-period-book-list')

    def test_admin_can_access_view(self):
        self.client.force_login(user=self.admin)

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        data = response.json()

       # self.assertEquals(len(data['results']), 1)
        #self.assertEquals(data['results'][0]['title'], 'book 1')