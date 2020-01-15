from rest_framework import routers
from .views import CoffeeTypeViewSet, FarmViewSet

router = routers.DefaultRouter()
router.register('api/coffee-type', CoffeeTypeViewSet, 'coffee-type')
router.register('api/farm', FarmViewSet, 'farm')
# router.register('api/stock', StockViewSet, 'stock')

urlpatterns = router.urls