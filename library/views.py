from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serializers
from . import filters
from . import script


class AuthorViewSet(ModelViewSet):
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    filter_backends = [SearchFilter]
    search_fields =['first_name', 'last_name', 'nationality']

    def update(self, request, *args, **kwargs):
        birth_date = request.data.get('birth_date')
        age = script.age_gt(birth_date, 18)
        if age:
            return Response(
                {'error': 'the age must be greeter than 18'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        birth_date = request.data.get('birth_date')
        age = script.age_gt(birth_date, 18)
        if age:
            return Response(
                {'error': 'the age must be greeter than 18'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

class BookViewSet(ModelViewSet):
    queryset = models.Book.objects.all()
    serializer_class = serializers.BookSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]

    filterset_class = filters.BookFilter
    search_fields = ['title', 'author', 'category']
    ordering_fields = ['title','id','num_exist','author']

    def create(self, request, *args, **kwargs):
        num = request.data.get('num_exist')
        published_date = request.data.get('published_date')
        if not script.positive_number(num):
            return Response({'error': 'the number of book must be greeter than 0'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        if  script.be_future(published_date):
            return Response({'error': 'the published date can not be future'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        return super().create(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        num = request.data.get('num_exist')
        published_date = request.data.get('published_date')

        if not script.positive_number(num):
            return Response({'error': 'the number of book must be greeter than 0'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        if  script.be_future(published_date):
            return Response({'error': 'the published date can not be future'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        return super().create(request, *args, **kwargs)

class CategoryViewSet(ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
