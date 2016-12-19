# Django
from django.conf.urls import url, include

# Core
from core.routers import router

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
