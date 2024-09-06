from rest_framework.serializers import ModelSerializer
from . import models


class CategorySerializer(ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class CommentSerializer(ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'

class SimpleBookSerializer(ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = models.Book
        fields = ('title', 'category', 'isbn', 'published_date')

class AuthorSerializer(ModelSerializer):
    book = SimpleBookSerializer(many=True, read_only=True)
    class Meta:
        model = models.Author
        fields = ('id', 'first_name', 'last_name', 'birth_date', 'biography', 'nationality', 'website', 'book')

class SimpleAuthorSerializer(ModelSerializer):
    class Meta:
        model = models.Author
        fields = ('first_name', 'last_name', 'birth_date', 'biography', 'nationality', 'website')

class BookSerializer(ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    category = CategorySerializer()
    author = SimpleAuthorSerializer()
    class Meta:
        model = models.Book
        fields = ('id', 'title', 'author', 'category', 'published_date', 'isbn','num_exist', 'comments')
