from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserQueryHistory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "password2")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user


class UserQueryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQueryHistory
        fields = "__all__"
