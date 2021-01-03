from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from user.serializers import *

from village.models import Article, Comment


class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    contents = serializers.CharField()
    user = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)

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

    def get_user(self, article):
        try:
            return UserSerializer(article.user, context=self.context).data

        except ObjectDoesNotExist:
            return serializers.ValidationError("no such user")

    def create(self, validated_data):
        return Article.objects.create(**validated_data)



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
