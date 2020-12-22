from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    user = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
    category = models.ForeignKey(ArticleCategory, related_name='article', on_delete=models.CASCADE)


class ArticleCategory(models.Model): #ToBeDiscussed
    CategoryArticle = models.TextChoices('CategoriesArticle',
                                    '동네사건사고'
                                    '동네생활이야기'
                                    '분실/실종센터'
                                    '우리동네질문')
    category_article = models.CharField(primary_key=True, choices=CategoryArticle.choices, max_length=10)


class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comment', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='content', on_delete=models.CASCADE)
    content = models.CharField(max_length=100, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True) #ToBeDiscussed


class LikeArticle(models.Model):
    user = models.ForeignKey(User, related_name='like_article', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, related_name='like_article', on_delete=models.CASCADE)
    # created_at = models.DateTimeField(auto_now_add=True) #ToBeDiscussed

    class Meta:
        unique_together = (
            ('user','article')
        )



