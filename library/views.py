from datetime import timedelta
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from accounts.models import Users
from accounts.permissions import IsAdminUser, IsBorrowerUser
from . import models
from . import serializers
from . import filters
from . import script

class UsersPagination(PageNumberPagination):
    page_size = 10
    ordering = ['id']  # Default ordering


# just admin access this class
class AuthorViewSet(ModelViewSet):
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    permission_classes = [IsAdminUser]
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

 # admin and borrower access this
class BookViewSet(ModelViewSet):
    queryset = models.Book.objects.all()
    serializer_class = serializers.BookSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UsersPagination
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


# just admin access this
class CategoryViewSet(ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ['name']


#just borrower access this
class AddCommentView(generics.CreateAPIView):
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [IsBorrowerUser]

    def perform_create(self, serializer):
        book = models.Book.objects.get(pk=self.kwargs['pk'])
        serializer.save(user=self.request.user, book=book)


class AddLendingTransactionView(generics.CreateAPIView):
    queryset = models.LendingTransaction.objects.all()
    serializer_class = serializers.LendingTransactionSerializer
    permission_classes = [IsBorrowerUser]
    def perform_create(self, serializer):
        user = self.request.user
        profile = Users.objects.get(id=user.id)

        max_borrowed_book = profile.max_borrowed_book
        current_borrowed_books = models.LendingTransaction.objects.filter(borrower=user, returned_at__isnull=True).count()

        if current_borrowed_books >= max_borrowed_book:
            return Response({'error':'You have reached the limit of borrowed books'},
                            status=status.HTTP_400_BAD_REQUEST)

        book = models.Book.objects.get(pk=self.kwargs['pk'])
        book.num_exist -= 1

        borrowed_at = timezone.now()

        loan_period_days = book.loan_period
        returned_at = borrowed_at + timedelta(days=loan_period_days)

        book.save()
        serializer.save(borrower=self.request.user,borrowed_at=borrowed_at,returned_at=returned_at,book=book)

class LendingTransactionUpdateView(generics.UpdateAPIView):
    queryset = models.LendingTransaction.objects.all()
    serializer_class = serializers.LendingTransactionUpdate

    def perform_update(self, serializer):
        instance = serializer.save()

        if instance.status == 'borrowed' and instance.returned_at < timezone.now():
            user = instance.borrower
            user.is_active = False
            user.save()
            instance.returned_at = timezone.now()
            instance.save()
            return Response({'error': 'the return date has been passed, your account is now inactive '}, status=status.HTTP_400_BAD_REQUEST)
        instance.status = 'returned'
        instance.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class  AddLoanPeriodBook(ModelViewSet):
    queryset = models.Book.objects.filter(loan_period=0)
    serializer_class = serializers.SimpleBookSerializer
    permission_classes = [IsAdminUser]
    pagination_class = UsersPagination
