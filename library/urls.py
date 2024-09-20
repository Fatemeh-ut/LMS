from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('authors', views.AuthorViewSet, basename='author')
router.register('books', views.BookViewSet, basename='book')
router.register('category', views.CategoryViewSet, basename='category')
router.register('loanPeriod', views.AddLoanPeriodBook, basename='loan-period-book')

urlpatterns =[
    path('', include(router.urls)),
    path('books/<int:pk>/add-comment', views.AddCommentView.as_view(), name='add-comment'),
    path('books/<int:pk>/add-lending', views.AddLendingTransactionView.as_view()),
    path('lending-transaction/<int:pk>/return-book', views.LendingTransactionUpdateView.as_view()),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema-lib'),
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema-lib')),
]
