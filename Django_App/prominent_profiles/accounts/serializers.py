from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    This serializer enforces the uniqueness check beyond the standard django 'email' check.
    Create overrides django defaults to create a CustomUser as defined in accounts/models.py
    """
    date_of_birth = serializers.DateField()

    def validate_phone_number(self, value):
        if value and CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This mobile number is already registered.")
        return value

    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'date_of_birth', 'location', 'first_name', 'last_name',
                  'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials'
    }

    def validate(self, attrs):
        """
        Handles a login case of email or phone number.
        The '@' should be suitable as validation in VueJS covers this holistically beforehand.
        """

        user_input = attrs.get('email')
        password = attrs.get('password')
        print(user_input)
        print(password)
        user = None
        if user_input:
            if '@' in user_input:
                user = authenticate(request=self.context.get('request'), email=user_input, password=password)
            else:
                user = authenticate(request=self.context.get('request'), phone_number=user_input, password=password)
        print("user", user)
        if user is None:
            raise ValidationError(self.default_error_messages['no_active_account'])

        data = {}

        refresh = self.get_token(user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data
