# DRF
from rest_framework import routers, viewsets

# Core
from core.models import FileMetaObject
from core.serializers import FileMetaObjectSerializer


class FileMetaObjectViewSet(viewsets.ModelViewSet):
    queryset = FileMetaObject.objects.all()
    serializer_class = FileMetaObjectSerializer


router = routers.DefaultRouter()
router.register(r'files', FileMetaObjectViewSet)
