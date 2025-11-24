from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_api_key.models import APIKey
from .models import UserProfile

# Serializer for updating user info
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]

# Serializer for updating user profile
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["telegram_username", "phone_number", "telegram_linked"]

# Serializer for changing password
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

# Serializer for listing API keys (excludes actual key, shows prefix only)
class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'prefix', 'name', 'created', 'revoked']
        read_only_fields = ['id', 'prefix', 'created', 'revoked']

# Serializer for creating API keys
class APIKeyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True, help_text="Descriptive name for the API key")

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()

# Serializer for API key creation response (includes plaintext key once)
class APIKeyResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    api_key = serializers.CharField(read_only=True, help_text="The plaintext API key (only shown once)")
    prefix = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    revoked = serializers.BooleanField(read_only=True)