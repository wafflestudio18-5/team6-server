from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render

from village.models import *
from village.serializers import *

import datetime


class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        return self.permission_classes

    def create(self, request):

        user = request.user
        title = request.data.get('title')
        articles = Article.objects.filter(user_id=user, title=title)

        if articles.exists():
            return Response({"error": "article with same writer and title is invalid."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        article = serializer.save(user=user)

        data = serializer.data

        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):

        user = request.user
        article = get_object_or_404(Article, pk=pk)

        if user != article.user:
            return Response({"error": "Can't update other User's article"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(article, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.update(article, serializer.validated_data)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):

        article = get_object_or_404(Article, pk=pk)

        return Response(self.get_serializer(article).data)

    def list(self, request):

        articles = self.get_queryset().all()

        res_data = ArticleSerializer(articles, many=True).data

        return Response(res_data)

    def destroy(self, request, pk=None):
        user = request.user
        article = get_object_or_404(Article, pk=pk)

        if user != article.user:
            return Response({"error": "Can't update other User's article"}, status=status.HTTP_403_FORBIDDEN)

        article.delete()

        return Response({"message": "Successfully deleted."})

    @transaction.atomic
    @action(methods=['post'], detail=True)
    def like(self, request, pk=None):
        user = request.user
        article = get_object_or_404(Article, pk=pk)
        check = user.like_article.filter(article=article)

        if check.exist():
            user.like_article.remove(article)
            article.like_count -= 1
            article.save()

            return Response("You Unliked this article.", status=status.HTTP_200_OK)

        else:
            user.like_article.add(article)
            article.like_count += 1
            article.save()

            return Response("You liked this article.", status=status.HTTP_200_OK)


class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly(),)

    @action(detail=True, url_path='article')
    def list(self, request):
        article = Article.objects.get(pk=Comment.article.id)
        if not article:
            return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)

        comments = self.get_queryset().all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path='article')
    def retrieve(self, request, pk=None):

        article = Article.objects.get(pk=Comment.article.id)
        if not article:
            return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)

        comment = get_object_or_404(Comment, pk=pk)
        return Response(self.get_serializer(comment).data)

    @transaction.atomic
    @action(detail=True, url_path='article')
    def create(self, request):

        article = Article.objects.get(pk=Comment.article.id)
        if not article:
            return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, article=article)

        data = serializer.data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, url_path='article')
    def update(self, request, pk=None):

        comment = get_object_or_404(Comment, pk=pk)

        # 댓글쓴사람의 아이디 == 현재 업뎃할 댓글 아이디(리퀘스트 아이디)
        if Comment.user.id != comment:
            return Response("error: Cannot update others comment.", status=status.HTTP_400_BAD_REQUEST)

        article = Article.objects.get(pk=Comment.article.id)
        if not article:
            return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, article=article, pk=pk)

        data = serializer.data
        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):

        comment = get_object_or_404(Comment, pk=pk)

        if Comment.user.id != comment:
            return Response("error: Cannot delete others comment.", status=status.HTTP_400_BAD_REQUEST)

        article = Article.objects.get(pk=Comment.article.id)
        if not article:
            return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)

        comment.delete()
        comment.save()

        return Response("Deleted this Comment.", status=status.HTTP_200_OK)
