from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BCIViewSet, ParcelaViewSet, ValidacaoViewSet

router = DefaultRouter()
router.register(r'parcelas', ParcelaViewSet)
router.register(r'bcis', BCIViewSet)
router.register(r'validacoes', ValidacaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
