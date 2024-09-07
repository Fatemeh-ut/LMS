from rest_framework.serializers import ModelSerializer,Serializer
from rest_framework import serializers
from .models import Users


class UserLoginSerializer(Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSigninSerializer(Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()


class BorrowerSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']


class AdminSerializer(ModelSerializer):
    class Meta:
        model = Users
        #fields = '__all__'
        fields = ['id', 'role', 'username', 'first_name', 'last_name', 'email', 'is_active']

# password username email active firstname lastname role