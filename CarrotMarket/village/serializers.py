from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from user.serializers import *
from village.models import Article, CategoryOfArticle, Comment


class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    contents = serializers.CharField()

    user = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'contents',
            'user',
            'category',
            'like_count',
        )

    def validate(self, data):

        title = data.get('title')
        contents = data.get('contents')

        if title == "" or contents == "":
            return serializers.ValidationError("title and content cannot be empty")

        return data

    def get_user(self, article):
        try:
            return UserSerializer(article.user, context=self.context).data

        except ObjectDoesNotExist:
            return serializers.ValidationError("no such user")

    def get_category(self, article):
        try:
            context = self.context
            context['category_article'] = context['category']

            return CategoryOfArticleSerializer(article.category, context=context).data

        except ObjectDoesNotExist:
            return serializers.ValidationError("cannot determine category")


class CategoryOfArticleSerializer(serializers.ModelSerializer):
    category_article = serializers.IntegerField()

    class Meta:
        model = CategoryOfArticle
        fields = (
            'category_article',
        )


class CommentSerializer(serializers.ModelSerializer):
    contents = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'article',
            'contents',
            'created_at',
            'updated_at',
            'deleted_at',
        )

    read_only_fields = [
        'id',
        'created_at',
        'updated_at',
        'deleted_at',
    ]

    def get_article(self, comment, pk=None):
        article = comment.article.objects(pk=pk)
        return ArticleSerializer(article, context='context').data
