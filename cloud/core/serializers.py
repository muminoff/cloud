# DRF
from rest_framework import serializers

# Core
from core.models import FileMetaObject


class FileMetaObjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileMetaObject
        fields = (
            'id', 'storage', 'created_at',
            'modified_at', 'name', 'parent',
            'content_type', 'size'
        )
