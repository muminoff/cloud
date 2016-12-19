# DRF
from rest_framework import routers, viewsets
from rest_framework.response import Response

# Core
from core.models import Storage
from core.serializers import FileMetaSerializer


class MainStorageViewSet(viewsets.ViewSet):

    def list(self, request):
        storage = Storage.objects.get(owner=request.user.profile)
        queryset = storage.browse()
        return Response(serializer.data)


router = routers.DefaultRouter()
# router.register(r'browse', MainStorageViewSet)
