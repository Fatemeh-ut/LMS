from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
#router.register('borrower', views.BorrowerViewSet)
router.register('admin', views.AdminsViewSet)


urlpatterns=[
    path('', include(router.urls)),
    path('login', views.UserLogin.as_view()),
    path('register', views.UserRegisterView.as_view()),
    path('borrower-profile/', views.BorrowerProfile.as_view()),
    path('borrower-transaction/', views.BorrowerTransaction.as_view())

]
