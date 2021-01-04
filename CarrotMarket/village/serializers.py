from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from user.serializers import *

from village.models import Article, Comment


class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    contents = serializers.CharField()
    userprofile = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = (
            'userprofile',
            'id',
            'title',
            'contents',
            'category',
            'like_count',
        )

    def get_userprofile(self, article):
        data = UserProfileSerializer(article.user.userprofile, context=self.context).data
        data.pop('phone')
        try:
            return data

        except ObjectDoesNotExist:
            return serializers.ValidationError("no such user")

    def create(self, validated_data):
        return Article.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    contents = serializers.CharField(required=True, allow_blank=False)
    userprofile = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'user_id',
            'userprofile',
            'article_id',
            'id',
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

    def get_article_id(self, comment, pk=None):
        article_id = comment.article.objects(pk=pk).id
        return ArticleSerializer(article_id, context='context').data

    def get_userprofile(self, comment):
        data = UserProfileSerializer(comment.user.userprofile, context=self.context).data
        data.pop('phone')
        return data

