from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from api.serializers import CoffeeTypeSerializer, FarmSerializer
from api.models import CoffeeType, Farm, Stock

class CoffeeTypeViewSet(viewsets.ModelViewSet):
    queryset = CoffeeType.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    serializer_class = CoffeeTypeSerializer

class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    serializer_class = FarmSerializer

# class StockViewSet(viewsets.ModelViewSet):
#     queryset = Stock.objects.all()
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [BasicAuthentication]
#     serializer_class = StockSerializer

