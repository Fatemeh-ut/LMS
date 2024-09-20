from django.test import TestCase
from datetime import date
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

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
            'first_name': 'updated author',
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

class BookViewSetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='password123',
            role='borrower'
        )
        self.client.login(username='user', password='password123')
        self.url = reverse('book-list')
        self.author = models.Author.objects.create(
            first_name='author',
            last_name='test'
        )
        self.category = models.Category.objects.create(name='category')
        self.book = models.Book.objects.create(
            title='book test',
            author=self.author,
            category=self.category,
            num_exist=5,
            published_date= '2019-01-01'
        )

    def test_create_book_success(self):
        data_book = {
            'title': 'new book',
            'author': self.author.id,
            'category':self.category,
            'published_date': '2019-01-01',
            'num_exist': 2
        }
        response = self.client.post(self.url, data_book, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_book_invalid_number(self):
        self.client.login(username='user', password='user123')
        data_book = {
            'title':'invalid book',
            'author': self.author,
            'num_exist':-8,
        }
        response = self.client.post(self.url, data_book, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('the number of book must be greeter than 0', response.data['error'])

    def test_create_book_future_published_date(self):
        data_book = {
            'title':'invalid book',
            'author': self.author,
            'num_exist':4,
            'published_date':'2028-02-08'
        }
        response = self.client.post(self.url, data_book, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('the published date can not be future', response.data['error'])

    def test_update_book_success(self):
        update_url = reverse('book-detail', args=[self.book.id])
        update_data = {
            'title': 'update book',
            'author': self.author.id,
            'category':"category",
            'published_date': '2019-01-01',
            'num_exist': 2
        }
        response = self.client.put(update_url, update_data,  content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_book_invalid_number(self):
        update_url = reverse('book-detail', args=[self.book.id])
        update_data = {
            'title': 'update book',
            'author': self.author.id,
            'category': "category",
            'num_exist': -9,
            'published_date': '2019-01-01'
        }
        response = self.client.put(update_url, update_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('the number of book must be greeter than 0', response.data['error'])

    def test_update_book_future_published_date(self):
        update_url = reverse('book-detail', args=[self.book.id])
        update_data = {
            'title': 'update book',
            'author': self.author.id,
            'category': "category",
            'num_exist': 8,
            'published_date': '2029-01-01'
        }
        response = self.client.patch(update_url, update_data,content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('the published date can not be future', response.data['error'])
       
    def test_delete_book(self):
        book = models.Book.objects.create(
            title='book delete test',
            author=self.author,
            num_exist=5
        )
        delete_url = reverse('book-detail', args=[book.id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Book.objects.filter(id = book.id))


class CategoryViewSetTest(APITestCase):
    def setUp(self):
        self.admin_user= User.objects.create_superuser(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.user = User.objects.create_user(
            username='user',
            password='user123',
            role='borrower'
        )
        self.url = reverse('category-list')
        models.Category.objects.create(name='Science')
        models.Category.objects.create(name='Fiction')
        models.Category.objects.create(name='category1')


    def test_admin_access(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 3)

    def test_user_not_access(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category(self):
        self.client.login(username='admin', password='admin123')
        category_data = {'name':'History'}
        response = self.client.post(self.url, category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Category.objects.count(), 4)
        self.assertEqual(models.Category.objects.last().name, 'History')

    def test_update_category(self):
        self.client.login(username='admin', password='admin123')
        category = models.Category.objects.create(name='old category')
        update_url = reverse('category-detail', args=[category.id])

        update_data = {'name': 'update name'}
        response = self.client.put(update_url, update_data, foramt='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, 'update name')
    def test_delete_category(self):
        self.client.login(username='admin', password='admin123')
        category = models.Category.objects.create(name = 'Test delete category')
        delete_url = reverse('category-detail', args=[category.id])

        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Category.objects.filter(id=category.id))

    def test_search_category(self):
        self.client.login(username='admin', password='admin123')
        search_url = f"{self.url}?search=Fiction"
        response = self.client.get(search_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Fiction')

class AddCommentTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.borrower = User.objects.create_user(
            username='borrower',
            password='password!0',
            role='borrower'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.comment = {
            'content':'test comment'
        }
        self.author = models.Author.objects.create(
            first_name='author',
            last_name='test',
        )
        self.book = models.Book.objects.create(
            title='book',
            author=self.author,
            num_exist=4
        )
        self.url = reverse('add-comment', kwargs={'pk':self.book.pk})
    def test_user_can_add_comment(self):
        self.client.login(username='borrower', password='password!0')
        response = self.client.post(self.url, self.comment, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = models.Comment.objects.get(book=self.book)
        self.assertEqual(comment.content, 'test comment')
        self.assertEqual(comment.user, self.borrower)

    def test_non_user_can_not_add_comment(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(self.url, self.comment, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AddTransactionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(

        )
    def test_borrower_access(self):
        pass
    def test_borrower_add_transaction(self):
        pass

 #
class AddTransactionUpdate(TestCase):
    pass
  #
class AddLoanPeriodTest(TestCase):
    pass    


