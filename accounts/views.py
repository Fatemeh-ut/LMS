from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Users
from . import serializers
from .permissions import IsAdminUser


class UserLogin(APIView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'],
                                password=serializer.validated_data['password'])

            if user is not None:
                if isinstance(user, Users):
                    refresh = RefreshToken.for_user(user)
                    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'no such username or password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    pass


class UserSignin(APIView):
    pass


class AdminsViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = serializers.AdminSerializer
    permission_classes = [IsAdminUser]


class BorrowerProfile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = serializers.BorrowerSerializer(user)
        return Response(serializer.data)


