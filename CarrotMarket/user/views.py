from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.models import UserProfile
from user.serializers import UserSerializer, UserProfileSerializer
from village.models import LikeArticle, Article
from village.serializers import ArticleSerializer, CommentSerializer
from user.region import *
from .models import User, UserProfile
import requests

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

        data = request.data
        usertype = request.POST.get('user_type', 'django')

        if usertype != 'kakao' and usertype != 'django' and usertype !='':
            return Response({"error": "wrong usertype: usertype must be 'django' or 'kakao'"}, status=status.HTTP_400_BAD_REQUEST)
        if usertype =='kakao':
            access_token= request.POST.get('access_token', '')

            if access_token == '' or None:
                return Response({"error": "Received no access token in request"}, status=status.HTTP_400_BAD_REQUEST)

            profile_request = requests.post(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile_json = profile_request.json()

            if profile_json == None:
                return Response({"error": "Received no response from Kakao database"}, status=status.HTTP_404_NOT_FOUND)

            try:# parsing json
                kakao_account = profile_json.get("kakao_account")
                email = kakao_account.get("email", None)
                profile = kakao_account.get("profile")
                username = profile.get("nickname")
 #               profile_image = profile.get("thumbnail_image_url")
            except KeyError:
                return Response({"error": "Need to agree to terms"}, status=status.HTTP_400_BAD_REQUEST)

            if (User.objects.filter(username=username).exists()): #기존에 가입된 유저가 카카오 로그인
                user = User.objects.get(username = username)
                login(request, user)

                if usertype == 'django':
                    User.objects.filter(username=username).update(email=email)  ###
                    UserProfile.objects.filter(user=user).update(nickname=username, user_type='kakao')  ###

                # 위치 옮김
                data = self.get_serializer(user).data
                token, created = Token.objects.get_or_create(user=user)
                data['token'] = token.key

                return Response(data, status=status.HTTP_200_OK)
            else: #신규 유저의 카카오 로그인
                data = {"username": username, "email": email, "user_type": 'kakao'}  ###
#               data['profile_image'] = profile_image

        area_data = get_area_information(request.data)

        if area_data['error_occured'] == "latlng_miss":
            return Response({"message": "latalang information is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if area_data['error_occured'] == "api response not OK":
            return Response({"error": "Can't get location"}, status=status.HTTP_400_BAD_REQUEST)
        
        if area_data['error_occured'] == "something is wrong":
            return Response({"error": "some component missing"}, status=status.HTTP_400_BAD_REQUEST)

        data["area"] = area_data["formatted_address"]

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['user_type'] == '':
            serializer.validated_data['user_type'] = 'django'

        try:
            user = serializer.save()
        except IntegrityError:
            return Response({"error": "A user with that username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        data = serializer.data
        data['token'] = user.auth_token.key
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


    # GET /user/me or user_id/articles/ # 내가 작성한 피드
    @action(detail=True, methods=['GET'])
    def articles(self, request, pk=None):
        if pk == 'me':
            user = request.user
        else:
            user = get_object_or_404(User, pk=pk)
        articles = user.article
        data = ArticleSerializer(articles, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    # GET /user/me or user_id/likearticle/ # 내가 좋아요를 누른 피드
    @action(detail=True, methods=['GET'])
    def like_articles(self, request, pk=None):
        if pk == 'me':
            user = request.user
        else:
            user = get_object_or_404(User, pk=pk)

        articles = Article.objects.filter(like_article__user=user)

        data = ArticleSerializer(articles, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    # GET /user/me or user_id/comments/ # 내가 작성한 댓글
    @action(detail=True, methods=['GET'])
    def comments(self, request, pk=None):
        if pk == 'me':
            user = request.user
        else:
            user = get_object_or_404(User, pk=pk)

        comments = user.comment
        data = CommentSerializer(comments, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_path='location', url_name='get_location') 

    def get_location(self, request, pk=None):
        
        if pk != 'me':
            return Response({"error": "Can't get other Users location"}, status=status.HTTP_400_BAD_REQUEST)

        data = get_area_information(request.data)

        if data['error_occured'] == "latlng_miss":
            return Response({"message": "latalang information is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if data['error_occured'] == "api response not OK":
            return Response({"error": "Can't get location"}, status=status.HTTP_400_BAD_REQUEST)
        
        if data['error_occured'] == "something is wrong":
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
        

