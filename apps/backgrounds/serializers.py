from rest_framework import serializers
from .models import Background


class BackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Background
        fields = ['key', 'name', 'description', 'image_path']