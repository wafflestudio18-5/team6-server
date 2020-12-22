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
    user = models.ForeignKey(User, related_name='buy', on_delete=models.CASCADE)
    product = models.OneToOneField(Product, related_name='buy', on_delete=models.CASCADE)
    sold_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('user', 'product')
        )


class LikeProduct(models.Model):
    user = models.ForeignKey(User, related_name='like_product', on_delete=models.CASCADE)
    article = models.ForeignKey(Product, related_name='like_product', on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('user','article')
        )



class CategoryProduct(models.Model): #ToBeDiscussed
    CATEGORIES_PRODUCT = models.TextChoices('CATEGORIES_PRODUCT',
                                            '디지털/가전'
                                            '가구/인테리어'
                                            '유아동/유아도서'
                                            '생활/가공식품'
                                            '스포츠/레저'
                                            '여성잡화'
                                            '여성의류'
                                            '남성패션/잡화'
                                            '게임/취미'
                                            '뷰티/미용'
                                            '반려동물용품'
                                            '도서/티켓/음반'
                                            '식물'
                                            '기타중고물품'
                                            '삽니다')
    categories_product = models.CharField(primary_key=True, choices=CATEGORIES_PRODUCT.choices, max_length=10)
