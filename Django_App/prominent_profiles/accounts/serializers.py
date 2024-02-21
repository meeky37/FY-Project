from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
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