from datetime import datetime
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from library.serializers import LendingTransactionUpdate
from library.models import LendingTransaction
from .models import Users
from . import serializers
from .permissions import IsAdminUser, IsBorrowerUser


class UserLogin(APIView):
    serializer_class = serializers.UserLoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
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


class UserRegisterView(APIView):
    serializer_class = serializers.UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user': serializers.UserRegistrationSerializer(user).data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminsViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = serializers.AdminSerializer
    permission_classes = [IsAdminUser]

class AdminTransaction(ModelViewSet):
    queryset = LendingTransaction.objects.all()
    serializer_class = LendingTransactionUpdate
    permission_classes = [IsAdminUser]

class BorrowerProfile(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(responses=serializers.BorrowerSerializer)
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = serializers.BorrowerSerializer(user)
        return Response(serializer.data)

class BorrowerTransaction(generics.ListAPIView):
    serializer_class = LendingTransactionUpdate
    permission_classes = [IsBorrowerUser]
    def get_queryset(self):
        user = self.request.user
        return LendingTransaction.objects.filter(borrower = user)

class BorrowerNotification(generics.ListAPIView):
    serializer_class = LendingTransactionUpdate
    permission_classes = [IsBorrowerUser]
    def get_queryset(self):
        return LendingTransaction.objects.filter(returned_at__lt = timezone.now(), status = 'borrowed')
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        for item in data:
            if item['returned_at']:
                returned_at = timezone.make_aware(datetime.strptime(item['returned_at'], '%Y-%m-%dT%H:%M:%S.%fZ'))
                if timezone.now() > returned_at:
                    item['message'] = "This book has not been returned yet."
                else:
                    item['message'] = "This book has been returned."
            else:
                item['message'] = "This book has not been returned yet."

            return Response(data)