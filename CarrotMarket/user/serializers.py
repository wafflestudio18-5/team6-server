from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    userprofile = serializers.SerializerMethodField()



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
            'date_joined',
            'userprofile',

        )

    def get_userprofile(self, user):
        return UserProfileSerializer(user.userprofile, context=self.context).data

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
            api_exception.status_code = status.HTTP_400_BAD_REQUEST
            raise api_exception

        return data

    @transaction.atomic
    def create(self, validated_data):
        area = validated_data.pop('area', '')
        nickname = validated_data.pop('nickname', '')
        phone = validated_data.pop('phone', '')

        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)
        UserProfile.objects.create(user=user, area=area, nickname=nickname, phone=phone)

        return user

    def update(self, user, validated_data):
        area = validated_data.get('area')
        nickname = validated_data.get('nickname')
        phone = validated_data.get('phone')

        profile = user.userprofile
        if area is not None:
            profile.area = area
        if nickname is not None:
            profile.nickname = nickname
        if phone is not None:
            profile.phone = phone
        profile.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    area = serializers.CharField(required=False)
    nickname = serializers.CharField(required=False)
    phone = serializers.CharField(max_length=13,
                                  required=False,

                                  validators=[RegexValidator(regex=r'^[0-9]{3}-([0-9]{3}|[0-9]{4})-[0-9]{4}$',
                                                             message="Phone number must be entered in the format '000-0000-0000'",
                                                             )
                                              ]
                                  )
    class Meta:
        model = UserProfile
        fields = [
            'area',
            'nickname',
            'phone',
        ]

        def validate(self, data):
            profile_serializer = UserProfileSerializer(data=data, context=self.context)
            profile_serializer.is_valid(raise_exception=True)
            return data
