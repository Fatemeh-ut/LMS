from tkinter.font import names

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView
from . import views


router = DefaultRouter()
#router.register('borrower', views.BorrowerViewSet)
router.register(r'admin', views.AdminsViewSet, basename='admin')


urlpatterns=[
    path('', include(router.urls)),
    path('login', views.UserLogin.as_view(), name='login'),
    path('register', views.UserRegisterView.as_view(), name='register'),
    path('borrower-profile/', views.BorrowerProfile.as_view()),
    path('borrower-transaction/', views.BorrowerTransaction.as_view()),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema-account'),
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema-account')),



]
