from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from api.serializers import CoffeeTypeSerializer, FarmSerializer, StockSerializer, CropSerializer, WithdrawalSerializer
from api.models import CoffeeType, Farm, Stock, Crop

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

class StockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    serializer_class = StockSerializer
    
    def get_queryset(self):
        user = self.request.user 
        if user.profile.coffeex_manager:
            return Stock.objects.all() 
        return Stock.objects.filter(owner=user)

class CropViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    serializer_class = CropSerializer

    def get_queryset(self):
        user = self.request.user 
        if user.profile.coffeex_manager:
            return Crop.objects.all() 
        return Crop.objects.filter(stock__owner=user)
    
    def get_serializer_class(self):
        if self.action == 'withdrawal':
            return WithdrawalSerializer
        return super().get_serializer_class()

    @action(methods=['put'], detail=True)
    def withdrawal(self, request, pk=None):
        quantity = int(self.request.data.get("quantity"))
        crop = self.get_object()
        available_bags = crop.available_bags
        if quantity > available_bags:
            message = 'Quantidade de sacas não disponível. Quantidade disponível: {}'.format(available_bags)
            return Response({'message': message},
                            status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user
        if not crop.user_authorized(user):
            message = 'Você não esta autorizado a realizar esta operação'
            return Response({'message': message},
                            status=status.HTTP_403_FORBIDDEN)
        crop.withdrawal(quantity, user)
        serializer = self.get_serializer(crop)
        return Response(serializer.data)
