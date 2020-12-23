from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    seller = models.ForeignKey(User, related_name='product', on_delete=models.CASCADE)
    price = models.PositiveIntegerField(db_index=True)
    title = models.CharField(max_length=50, db_index=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_sold = models.BooleanField(default=False)


class Buy(models.Model):
    buyer = models.ForeignKey(User, related_name='buy', on_delete=models.CASCADE)
    product = models.OneToOneField(Product, related_name='buy', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('buyer', 'product')
        )


class LikeProduct(models.Model):
    user = models.ForeignKey(User, related_name='like_product', on_delete=models.CASCADE)
    article = models.ForeignKey(Product, related_name='like_product', on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('user','article')
        )



class CategoryOfProduct(models.Model): #ToBeDiscussed


    CATEGORY_PRODUCT = (

        (1,'디지털/가전'),
        (2,'가구/인테리어'),
        (3,'유아동/유아도서'),
        (4,'생활/가공식품'),
        (5,'스포츠/레저'),
        (6,'여성잡화'),
        (7,'여성의류'),
        (8,'남성패션/잡화'),
        (9,'게임/취미'),
        (10,'뷰티/미용'),
        (11,'반려동물용품'),
        (12,'도서/티켓/음반'),
        (13,'식물'),
        (14,'기타중고물품'),
        (15,'삽니다'),
    )
    category_product = models.PositiveSmallIntegerField(primary_key=True, choices=CATEGORY_PRODUCT)
