from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('authors', views.AuthorViewSet)
router.register('books', views.BookViewSet)
router.register('category', views.CategoryViewSet)

urlpatterns =[
    path('', include(router.urls)),
]
