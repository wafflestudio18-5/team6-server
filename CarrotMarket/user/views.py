from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from user.serializers import UserSerializer, UserProfileSerializer
from user.region import *


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(),)
        return super(UserViewSet, self).get_permissions()

    # POST /user/ 회원가입
    def create(self, request):

        user = request.user

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)


        try:
            user = serializer.save()
        except IntegrityError:
            return Response({"error": "A user with that username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        data = serializer.data
        data['token'] = user.auth_token.key

        data['userprofile'] = UserProfileSerializer(user.userprofile).data

        return Response(data, status=status.HTTP_201_CREATED)

    # PUT /user/login/  로그인
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            data = self.get_serializer(user).data
            token, created = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            return Response(data)

        return Response({"error": "Wrong username or wrong password"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['POST'])  # 로그아웃
    def logout(self, request):
        logout(request)
        return Response()

    # Get /user/{user_id} # 유저 정보 가져오기(나 & 남)
    def retrieve(self, request, pk=None):
        if pk == 'me':
            user = request.user
        else:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    # PUT /user/me/  # 유저 정보 수정 (나)
    def update(self, request, pk=None):
        if pk != 'me':
            return Response({"error": "Can't update other Users information"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(user, serializer.validated_data)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='location', url_name='get_location') 

    def get_location(self, request, pk=None):
        
        if pk != 'me':
            return Response({"error": "Can't get other Users location"}, status=status.HTTP_400_BAD_REQUEST)

        data = get_area_information(request.data)

        if data['error_occured'] == "latlng_miss":
            return Response({"message": "latalang information is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if data['error_occured'] == "api response not OK":
            return Response({"error": "Can't get location"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        userprofile_data = UserProfileSerializer(user.userprofile).data
        
        user_area = userprofile_data["area"]
        cur_area = data["formatted_address"]

        #print(user_area)
        #print(cur_area)

        if user_area!=cur_area:
            return Response({"error": "Could not match area"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)
        

