from rest_framework import serializers
from .models import ApiKey

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ['id', 'user', 'name', 'prefix', 'is_active', 'created_at']
        extra_kwargs = {
            'prefix': {'read_only': True},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        return ApiKey.objects.create(user=user, **validated_data)