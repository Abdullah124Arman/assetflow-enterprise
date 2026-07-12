from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password

class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    department_id = serializers.UUIDField(required=False, allow_null=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
