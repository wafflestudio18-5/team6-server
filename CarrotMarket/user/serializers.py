from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token

from user.models import UserProfile


class UserProfileSerializer(object):
    pass


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    joined_at = serializers.DateTimeField(read_only=True)
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'last_login',
            'joined_at',
            'profile',
        )

    def get_profile(self, user):
        return UserProfileSerializer(user.profile, context=self.context).data

    def validate_password(self, value):
        return make_password(value)

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if bool(first_name) ^ bool(last_name):
            api_exception = serializers.ValidationError("First name and last name should appear together.")
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception
        if first_name and last_name and not (first_name.isalpha() and last_name.isalpha()):
            api_exception = serializers.ValidationError("First name or last name should not have number.")
            api_exception.status_code = status.HTTP_404_BAD_REQUEST
            raise api_exception


        profile_serializer = UserProfileSerializer(data=data, context=self.context)
        profile_serializer.is_valid(raise_exception=True)
        return data

    @transaction.atomic
    def create(self, validated_data):
        area = validated_data.pop('area')
        kindness = validated_data.pop('kindness', None)
        nickname = validated_data.pop('nickname', '')
        phone = validated_data.pop('phone', '')

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)

        UserProfile.objects.create(user=user, area=area, kindness=kindness, nickname=nickname, phone=phone)

        return user

    def update(self, user, validated_data):
        user_profile = user.profile
        area = validated_data.get('area')
        kindness = validated_data.get('kindness')
        nickname = validated_data.get('nickname')
        phone = validated_data.get('phone')
        if area is not None or nickname is not None or phone is not None or kindness:
            if area is not None:
                user_profile.area = area
            if nickname is not None:
                user_profile.nickname = nickname
            if phone is not None:
                user_profile.phone = phone
            if kindness:
                user_profile.kindness = kindness
            user_profile.save()
        super(UserSerializer, self).update(user, validated_data)
