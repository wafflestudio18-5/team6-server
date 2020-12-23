from django.contrib.auth.models import User
from django.db import models

class UserProfile (models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    area = models.CharField(max_length=20,) #ToBeDiscussed
    kindness = models.PositiveSmallIntegerField(db_index=True)
    nickname = models.CharField(max_length=10, db_index=True)
    phone = models.CharField(max_length=11, db_index=True)
