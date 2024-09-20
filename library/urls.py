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
    path('lending-transactions/add/<int:pk>/', views.AddLendingTransactionView.as_view(), name='add-lending-transaction'),
    path('lending-transaction-update/<int:pk>', views.LendingTransactionUpdateView.as_view(), name='lending-transaction-update'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema-lib'),
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema-lib')),
]
