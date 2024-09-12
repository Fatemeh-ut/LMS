from enum import unique

from rest_framework.serializers import ModelSerializer,Serializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Users


class UserLoginSerializer(Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserRegistrationSerializer(Serializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = Users
        fields = ['username', 'password', 'password2', 'first_name', 'last_name', 'email']

    def validate(self, data):

        if data['password'] != data['password2']:
            raise serializers.ValidationError({'error':'passwords not match '})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = Users.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class BorrowerSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']


class AdminSerializer(ModelSerializer):
    class Meta:
        model = Users
        #fields = '__all__'
        fields = ['id', 'role', 'username', 'password', 'first_name', 'last_name', 'email', 'is_active']

# password username email active firstname lastname role