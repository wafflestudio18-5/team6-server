from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from rest_framework.routers import SimpleRouter

from village.models import *
from village.serializers import *

import datetime

class CursorSetPagination(CursorPagination):
    page_size = 5
    page_size_query_param = 'page_size'


class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated(),)
    pagination_class = CursorSetPagination

    def get_permissions(self):
        return self.permission_classes

    def create(self, request):

        user = request.user
        title = request.data.get('title')
        articles = Article.objects.filter(article_writer_id=user, title=title)

        if articles.exists():
            return Response({"error": "article with same writer and title is invalid."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(article_writer=user)

        data = serializer.data

        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):

        user = request.user
        article = get_object_or_404(Article, pk=pk)

        if user != article.article_writer:
            return Response({"error": "Can't update other User's article"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(article, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.update(article, serializer.validated_data)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):

        article = get_object_or_404(Article, pk=pk)

        return Response(self.get_serializer(article).data)

    def list(self, request):

        title = self.request.query_params.get('title')
        articles = self.get_queryset()


        if title:
            articles = articles.filter(title__icontains=title)

        data = ArticleSerializer(articles, many=True).data

        return Response(data)

    def destroy(self, request, pk=None):
        user = request.user
        article = get_object_or_404(Article, pk=pk)

        if user != article.article_writer:
            return Response({"error": "Can't delete other User's article"}, status=status.HTTP_403_FORBIDDEN)

        article.delete()

        return Response({"message": "Successfully deleted."})

    @transaction.atomic
    @action(methods=['post'], detail=True)
    def like(self, request, pk=None):
        user = request.user
        article = get_object_or_404(Article, pk=pk)
        check = user.like_article.filter(article=article)

        if check:
            LikeArticle.objects.get(user=user, article=article).delete()
            article.like_count = LikeArticle.objects.filter(article=article).count()
            article.save()

            return Response("You Unliked this article.", status=status.HTTP_200_OK)

        else:
            LikeArticle.objects.create(user=user, article=article)
            article.like_count = LikeArticle.objects.filter(article=article).count()
            article.save()

            return Response("You liked this article.", status=status.HTTP_200_OK)

    @transaction.atomic
    @action(methods=['POST'], detail=True, url_path='comment_write')
    def comment_write(self, request, pk=None):

        article = get_object_or_404(Article, pk=pk)
        user = request.user

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(comment_writer=user, article=article)
        data = serializer.data

        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=True, url_path='comment_list')
    def comment_list(self, request, pk=None):

        qp_contents = self.request.query_params.get('contents')

        article = get_object_or_404(Article, pk=pk)
        comments = article.comment.get_queryset()

        if qp_contents:
            comments = comments.filter(contents__icontains=qp_contents)

        return Response(CommentSerializer(comments, many=True).data)

    @action(methods=['GET'], detail=True, url_path='comment/(?P<comment_pk>[^/.]+)')
    def comment_retrieve(self, request, comment_pk, pk=None):

        article = get_object_or_404(Article, pk=pk)
        comment = get_object_or_404(article.comment, pk=comment_pk)

        return Response(CommentSerializer(comment).data)

    @action(methods=['PUT'], detail=True, url_path='comment_update/(?P<comment_pk>[^/.]+)')
    def comment_update(self, request, comment_pk, pk=None):
        user = request.user
        article = get_object_or_404(Article, pk=pk)
        comment = get_object_or_404(article.comment, pk=comment_pk)

        if user != comment.comment_writer:
            return Response({"error": "Can't Update other User's comment"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.update(comment, serializer.validated_data)

        return Response(serializer.data)

    @action(methods=['DELETE'], detail=True, url_path='comment_delete/(?P<comment_pk>[^/.]+)')
    def comment_delete(self, request, comment_pk, pk=None):
        user = request.user
        article = get_object_or_404(Article, pk=pk)
        comment = get_object_or_404(article.comment, pk=comment_pk)

        if user != comment.comment_writer:
            return Response({"error": "Can't delete other User's comment"}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()

        return Response({"message": "Successfully deleted."})

   
