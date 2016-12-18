# DRF
from rest_framework import serializers

# Core
from core.models import FileMeta


class FileMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileMeta
        fields = (
            'id', 'storage', 'created_at',
            'modified_at', 'name', 'parent',
            'content_type', 'size'
        )
