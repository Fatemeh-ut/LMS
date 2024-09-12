from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('authors', views.AuthorViewSet)
router.register('books', views.BookViewSet)
router.register('category', views.CategoryViewSet)
router.register('loanPeriod', views.AddLoanPeriodBook, basename='loan-period-book')

urlpatterns =[
    path('', include(router.urls)),
    path('books/<int:pk>/add-comment', views.AddCommentView.as_view()),
    path('books/<int:pk>/add-lending', views.AddLendingTransactionView.as_view())
]
