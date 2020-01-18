from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Stock, Crop, Withdrawal, Farm, CoffeeType

class CoffeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeType
        fields = ['id', 'name']

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ['id', 'name']

class StockSerializer(serializers.ModelSerializer):
    coffee_types = CoffeeTypeSerializer(many=True, read_only=True)
    origin_farms = FarmSerializer(many=True, read_only=True) 
    available_bags = serializers.IntegerField(read_only=True)
    withdrawal_quantity = serializers.IntegerField(read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Stock
        fields = [
            'id',
            'name',
            'owner',
            'coffee_types',
            'origin_farms',
            'capacity',
            'available_bags',
            'withdrawal_quantity'
        ]

class CropSerializer(serializers.ModelSerializer):
    available_bags = serializers.IntegerField(read_only=True)
    withdrawal_quantity = serializers.IntegerField(read_only=True)
    deposit_date = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Crop
        fields = [
            'id',
            'stock', 
            'coffee_type', 
            'farm', 
            'shelf_life', 
            'quantity', 
            'withdrawal_quantity',
            'available_bags',
            'deposit_date',
        ]

class WithdrawalSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()