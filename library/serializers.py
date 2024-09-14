
from rest_framework.serializers import ModelSerializer, SlugRelatedField, DateTimeField
from . import models


class CategorySerializer(ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class CommentSerializer(ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['content','rating']
        extra_kwargs = {
            'user': {'read_only': True},
            'book': {'read_only': True}
        }

class SimpleBookSerializer(ModelSerializer):
    category = SlugRelatedField(
        queryset=models.Category.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = models.Book
        fields = ('title', 'category', 'isbn', 'published_date', 'loan_period')
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.category = validated_data.get('category', instance.category)
        instance.isbn = validated_data.get('isbn', instance.isbn)
        instance.published_date = validated_data.get('published_date', instance.published_date)
        instance.loan_period = validated_data.get('loan_period', instance.loan_period)
        instance.save()
        return instance

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
    author = SimpleAuthorSerializer()
    category = SlugRelatedField(
        queryset=models.Category.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = models.Book
        fields = ('id', 'title', 'author', 'category', 'published_date', 'isbn','num_exist', 'comments', 'loan_period')

class LendingTransaction(ModelSerializer):
    class Meta:
        model = models.LendingTransaction
        fields = ['book', 'status']
        read_only = ['borrower', 'borrowed_at', 'returned_at']
        extra_kwargs = {
            'borrower': {'read_only': True},
            'book': {'read_only': True}
        }

class LendingTransactionUpdate(ModelSerializer):
    class Meta:
        model = models.LendingTransaction
        fields = ['book','borrowed_at', 'returned_at', 'status']