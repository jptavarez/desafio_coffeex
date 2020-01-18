from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from api.serializers import CoffeeTypeSerializer, FarmSerializer, StockSerializer, CropSerializer, WithdrawalSerializer
from api.models import CoffeeType, Farm, Stock, Crop

class CoffeeTypeViewSet(viewsets.ModelViewSet):
    queryset = CoffeeType.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    serializer_class = CoffeeTypeSerializer

class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    serializer_class = FarmSerializer

class StockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    serializer_class = StockSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        """
            Overriding "perform_update" to make validations before updating
        """
        capacity = serializer.validated_data['capacity']
        stock = serializer.instance
        if capacity < stock.available_bags:
            message = 'A capacidade do estoque não pode ser menor que a quantidade de sacas disponível no estoque.'
            raise ValidationError({'capacity': message})
        
        if not stock.user_authorized(self.request.user):
            message = 'O usuário não possuí permissão para atualizar esse estoque.'
            raise ValidationError({'stock': message})
        serializer.save()
    
    def perform_destroy(self, stock):
        """
            Overriding "perform_destroy" to make validations before deleting
        """
        if not stock.user_authorized(self.request.user):
            message = 'O usuário não possuí permissão para deletar esse estoque.'
            raise ValidationError({'stock': message})
        if stock.available_bags > 0:
            message = 'Não é possível deletar um estoque que possui sacas disponíveis.'
            raise ValidationError({'stock': message})
        stock.delete()
    
    def get_queryset(self):
        """
            Overriding "get_queryset" to make sure that it will be listed only stocks that
            the user is allowed to access.
        """
        user = self.request.user 
        if user.profile.coffeex_manager:
            return Stock.objects.all() 
        return Stock.objects.filter(owner=user)
    
    def get_object(self):
        """
            Overriding "get_object" to make sure that the users will not be allowed to access
            a stock that they don't have permission.
        """
        stock = super().get_object()
        user = self.request.user
        if not stock.user_authorized(user):
            raise PermissionDenied('Usuário não autorizado.')
        return stock

class CropViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    serializer_class = CropSerializer

    def get_queryset(self):
        """
            Overriding "get_queryset" to make sure that it will be listed only crops that
            the user is allowed to access.
        """
        user = self.request.user 
        if user.profile.coffeex_manager:
            return Crop.objects.all() 
        return Crop.objects.filter(stock__owner=user)
    
    def get_serializer_class(self):
        if self.action == 'withdrawal':
            return WithdrawalSerializer
        return super().get_serializer_class()
    
    def get_object(self):
        """
            Overriding "get_object" to make sure that the users will not be allowed to access
            a crop that they don't have permission.
        """
        crop = super().get_object()
        user = self.request.user
        if not crop.user_authorized(user):
            raise PermissionDenied('Usuário não autorizado.')
        return crop
    
    def perform_create(self, serializer):
        """
            Overriding "perform_create" to make validations before inserting
        """
        quantity = serializer.validated_data['quantity']
        stock = serializer.validated_data['stock']
        stock = Stock.objects.get(pk=stock.id)
        
        if not stock.user_authorized(self.request.user):
            message = 'O usuário não possuí permissão para utilizar esse estoque.'
            raise ValidationError({'stock': message})
        
        available_space = stock.available_space
        if quantity > available_space:
            message = 'Espaço insuficiente no estoque. Espaço disponível: {}'.format(available_space)
            raise ValidationError({'quantity': message})
        
        serializer.save()    
    
    @action(methods=['put'], detail=True)
    def withdrawal(self, request, pk=None):
        
        serializer = WithdrawalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.data['quantity']
        
        crop = self.get_object()
        available_bags = crop.available_bags
        if quantity > available_bags:
            message = 'Quantidade de sacas não disponível. Quantidade disponível: {}'.format(available_bags)
            raise ValidationError({'quantity': message})
    
        crop.withdrawal(quantity)
        serializer = CropSerializer(crop)
        return Response(serializer.data)
