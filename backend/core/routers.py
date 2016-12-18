# DRF
from rest_framework import routers, viewsets

# Core
from core.models import FileMeta
from core.serializers import FileMetaSerializer


class FileMetaViewSet(viewsets.ModelViewSet):
    queryset = FileMeta.objects.all()
    serializer_class = FileMetaSerializer


router = routers.DefaultRouter()
router.register(r'files', FileMetaViewSet)
