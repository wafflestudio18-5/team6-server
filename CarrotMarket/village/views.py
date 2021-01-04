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
from rest_framework.routers import SimpleRouter

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
        serializer.save(user=user)

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

        title = self.request.query_params.get('title')
        articles = self.get_queryset().all()

        if title:
            articles = articles.filter(title__icontains=title)

        data = ArticleSerializer(articles, many=True).data

        return Response(data)

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
    @action(methods=['POST'], detail=True, url_path='write_comment')
    def write_comment(self, request, pk=None):

        article = get_object_or_404(Article, pk=pk)
        user = request.user

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, article=article)
        data = serializer.data
        return Response(data, status=status.HTTP_201_CREATED)

    # # @action(url_path=SimpleRouter.register('comment'), CommentViewSet)...?
    # class CommentViewSet(viewsets.GenericViewSet):
    #     queryset = Comment.objects.all()
    #     serializer_class = CommentSerializer
    #     permission_classes = (IsAuthenticatedOrReadOnly(),)
    #
    #     @transaction.atomic
    #     @action(methods=['POST'], detail=True, url_path='comment')
    #     def comment(self, request, pk=None):
    #
    #         article = get_object_or_404(Article, pk=pk)
    #
    #         if not article:
    #             return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)
    #
    #         serializer = self.get_serializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save(user=request.user, article=article)
    #         data = serializer.data
    #         return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, url_path='list_comments')
    def list_comments(self, request, pk=None):

        article = get_object_or_404(Article, pk=pk)
        # comments = Comment.objects.filter(article_id=article.id)
        user = request.user
        comments = article.comment.get_queryset()
        # 에러 : 쿼리셋에 유저가 없다.
        return Response(CommentSerializer(comments).data)
    #
    # @action(detail=True, url_path='article')
    # def retrieve(self, request, pk=None):
    #
    #     article = Article.objects.get(pk=Comment.article.id)
    #     if not article:
    #         return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)
    #
    #     comment = get_object_or_404(Comment, pk=pk)
    #     return Response(self.get_serializer(comment).data)
    #
    # @action(detail=True, url_path='article')
    # def update(self, request, pk=None):
    #
    #     comment = get_object_or_404(Comment, pk=pk)
    #
    #     # 댓글쓴사람의 아이디 == 현재 업뎃할 댓글 아이디(리퀘스트 아이디)
    #     if Comment.user.id != comment:
    #         return Response("error: Cannot update others comment.", status=status.HTTP_400_BAD_REQUEST)
    #
    #     article = Article.objects.get(pk=Comment.article.id)
    #     if not article:
    #         return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)
    #
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=request.user, article=article, pk=pk)
    #
    #     data = serializer.data
    #     return Response(data, status=status.HTTP_201_CREATED)
    #
    # def destroy(self, request, pk=None):
    #
    #     comment = get_object_or_404(Comment, pk=pk)
    #
    #     if Comment.user.id != comment:
    #         return Response("error: Cannot delete others comment.", status=status.HTTP_400_BAD_REQUEST)
    #
    #     article = Article.objects.get(pk=Comment.article.id)
    #     if not article:
    #         return Response("error: This article doesn't exist anymore", status=status.HTTP_404_NOT_FOUND)
    #
    #     comment.delete()
    #     comment.save()
    #
    #     return Response("Deleted this Comment.", status=status.HTTP_200_OK)
