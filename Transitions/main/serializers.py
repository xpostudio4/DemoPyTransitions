from rest_framework import serializers
from main.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'user_state'
        ]


class InviteSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False, max_length=100)
    email = serializers.CharField(required=True, allow_blank=False, max_length=100)
