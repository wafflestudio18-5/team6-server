from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.views.generic import detail
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from village.models import Comment, Article, LikeArticle
from village.serializers import CommentSerializer, ArticleSerializer, LikeArticleSerializer


class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        return self.permission_classes

    def create(self, request):

        title = request.data.get('title')
        content = request.data.get('content')

        if not title or not content:
            return Response({"message": "title and content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        articles = Article.objects.filter(user_id=user, title=title)

        if articles.exists():
            return Response({"error": "article with same writer and title is invalid."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            article = serializer.save()
        except AttributeError:
            return Response({"error": "check information."}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.data

        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):

        article = get_object_or_404(Article, pk=pk)

        serializer = self.get_serializer(article, data=request.data, partial=True)
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

        article = Article.objects.filter(user_id=user, title=title)

        if not article.exists():
            return Response({"error": "There is no such article."}, status=status.HTTP_400_BAD_REQUEST)

        article.delete()

        return Response({"message": "Successfully deleted."})

    @action(detail=True, method=['POST'], url_path='like')
    def like_article(self, request, pk=None):
        user = request.user
        article = get_object_or_404(Article, pk=pk)
        check = user.like_article.filter(article=article)

        if check.exist():
            user.like_article.remove(article)
            article.like_count -= 1
            article.save()
        else:
            user.like_article.remove(article)
            article.like_count += 1
            article.save()

        return Response(status=status.HTTP_200_OK)


class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly(),)

    @action(detail=True, url_path='article')
    def list(self, request):
        comments = self.get_queryset().all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path='article')
    def retrieve(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        return Response(self.get_serializer(comment).data)

    @action(detail=True, url_path='article')
    def create(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = serializer.data
        return Response(data, status=status.HTTP_201_CREATED)
