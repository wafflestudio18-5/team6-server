from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from user.serializers import *
from village.models import Article,CategoryOfArticle

class ArticleSerializer(serializers.ModelSerializer):
    title = serializer.CharField()
    content = serializer.CharField()
    user = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'content',
            'user',
            'category',
        )
    
    def validate(self, data):
        
        title = data.get('title')
        content = data.get('content')

        if title == "" or content == ""
            return serializers.ValidationError("title and content cannot be empty")

        return data
    
    def get_user(self, article):
        try:
            return UserSerializer(article.user,context=self.context).data
        except ObjectDoesNotExist:
            return serializers.ValidationError("no such user")

    def get_category(self, article):
        try:
            context = self.context
            context['category_article'] = context['category']
            return CategoryOfArticleSerializer(article.category,context=context).data
        
        except ObjectDoesNotExist:
            return serializers.ValidationError("cannot determine category")

class CategoryOfArticleSerializer(serializers.ModelSerializer):
    category_article = serializer.IntegerField()

    class Meta:
        model = CategoryOfArticle
        fields = (
            'category_article',
        )
    
    def validate(self, data):

        return data