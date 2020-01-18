from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from django.urls import include, path
from .views import CoffeeTypeViewSet, FarmViewSet, StockViewSet, CropViewSet

router = routers.DefaultRouter()
router.register('api/coffee-type', CoffeeTypeViewSet, 'coffee-type')
router.register('api/farm', FarmViewSet, 'farm')
router.register('api/stock', StockViewSet, 'stock')
router.register('api/crop', CropViewSet, 'crop')

urlpatterns = router.urls
urlpatterns.append(path('docs/', include_docs_urls(title='Desafio Estoque API')))
