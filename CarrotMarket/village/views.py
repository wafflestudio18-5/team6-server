from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render

from village.models import *
from village.serializers import *

import datetime

class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated(), )    

    def get_permissions(self):
        return self.permission_classes

    def create(self, request):

        title = request.data.get('title')
        content = request.data.get('content')

        if not title or not content:
            return Response({"error": "title and content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)            

        user = request.user

        articles = Article.objects.filter(user_id=user,title=title)

        if articles:
            return Response({"error": "article with same writer and title is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try :
            article = serializer.save()
        except AttributeError:
            return Response({"error": "check informations."}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.data

        return Response(data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk = None):
        
        article = get_object_or_404(Article, pk=pk)

        serializer = self.get_serializer(article, data=request.data, partial = True)
        serializer.is_valid(raise_exception=True)

        serializer.update(article, serializer.validated_data)

        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):

        article = get_object_or_404(Article, pk=pk)

        return Response(self.get_serializer(article).data)


    def list(self, request):
        
        articles = Article.objects.all()
        
        res_data = ArticleSerializer(articles, many=True).data

        return Response(res_data)

    def destroy(self, request, pk=None):

        user = request.user
        title = request.data.get('title')

        article = Article.objects.filter(user_id=user,title=title)

        if not article
            return Response({"error": "There is no such article."}, status=status.HTTP_400_BAD_REQUEST)

        article.delete()

        return Response({"error": "Successfully deleted."})



    



# Create your views here.
