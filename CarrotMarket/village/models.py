from django.contrib.auth.models import User
from django.db import models

class Article(models.Model):
    CATEGORY_ARTICLE = (
        (1, '동네사건사고'),
        (2, '동네생활이야기'),
        (3, '분실/실종센터'),
        (4, '우리동네질문'),
    )
    article_writer = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
    # category = models.ForeignKey(CategoryOfArticle, related_name='article', on_delete=models.CASCADE)
    category = models.PositiveSmallIntegerField(choices=CATEGORY_ARTICLE)
    contents = models.TextField(db_index=True)
    title = models.CharField(max_length=50, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comment', on_delete=models.CASCADE)
    comment_writer = models.ForeignKey(User, related_name='comment', on_delete=models.CASCADE)

    contents = models.CharField(max_length=100, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class LikeArticle(models.Model):
    user = models.ForeignKey(User, related_name='like_article', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, related_name='like_article', on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('user', 'article')
        )
