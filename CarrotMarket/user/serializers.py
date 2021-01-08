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
    user_type = serializers.CharField(write_only=True, allow_blank=True, required=False, default = 'django')
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(read_only=True)
    joined_at = serializers.DateTimeField(read_only=True)
    userprofile = serializers.SerializerMethodField()
    area = serializers.CharField(write_only=True, allow_blank=True, required=False)
    nickname = serializers.CharField(write_only=True, allow_blank=True, required=False)
    phone = serializers.CharField(write_only=True,
                                  allow_blank=True,
                                  max_length=13,
                                  required=False,
                                  validators=[RegexValidator(regex=r'^[0-9]{3}-([0-9]{3}|[0-9]{4})-[0-9]{4}$',
                                                             message="Phone number must be entered in the format '000-0000-0000'",
                                                             )
                                              ]
                                  )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'user_type',
            'email',
            'password',
            'first_name',
            'last_name',
            'last_login',
            'joined_at',
            'userprofile',
            'area',
            'nickname',
            'phone',
        )

    def get_userprofile(self, user):
        return UserProfileSerializer(user.userprofile, context=self.context).data #여기서 오류 AttributeError: 'collections.OrderedDict' object has no attribute 'userprofile' 넘겨주는 값 잘못되었

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

        profile_serializer = UserProfileSerializer(data=data, context=self.context)
        profile_serializer.is_valid(raise_exception=True)
        return data

    @transaction.atomic
    def create(self, validated_data):
        area = validated_data.pop('area', '')
        nickname = validated_data.pop('nickname', '')
        phone = validated_data.pop('phone', '')
        user_type = validated_data.pop('user_type', '')
        user = super(UserSerializer, self).create(validated_data)
        Token.objects.create(user=user)
        UserProfile.objects.create(user=user, area=area, nickname=nickname, phone=phone, user_type = user_type)

        return user

    def update(self, user, validated_data):
        area = validated_data.get('area')
        nickname = validated_data.get('nickname')
        phone = validated_data.get('phone')
#        user_type = validated_data.pop('user_type', '')

        profile = user.userprofile
        if area is not None:
            profile.area = area
        if nickname is not None:
            profile.nickname = nickname
        if phone is not None:
            profile.phone = phone
#        if user_type is not None:
#            profile.user_type = user_type
        profile.save()

        return super(UserSerializer, self).update(user, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField(allow_blank=True, required=False, default = 'django')
    area = serializers.CharField(allow_blank=True, required=False)
    nickname = serializers.CharField(allow_blank=True, required=False)
    phone = serializers.CharField(allow_blank=True, max_length=13,
                                  required=False,
                                  validators=[RegexValidator(regex=r'^[0-9]{3}-([0-9]{3}|[0-9]{4})-[0-9]{4}$',
                                                             message="Phone number must be entered in the format '000-0000-0000'",
                                                             )
                                              ]
                                  )

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user_type',
            'area',
            'nickname',
            'phone',
        ]