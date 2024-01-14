from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField()
    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'date_of_birth', 'location', 'first_name', 'last_name',
                  'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user