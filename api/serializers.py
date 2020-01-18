from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Stock, Crop, Withdrawal, Farm, CoffeeType

class CoffeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeType
        fields = '__all__'

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    coffee_types = CoffeeTypeSerializer(many=True, read_only=True)
    origin_farms = FarmSerializer(many=True, read_only=True) 
    available_bags = serializers.IntegerField(read_only=True)
    withdrawal_quantity = serializers.IntegerField(read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Stock
        fields = '__all__'

class CropSerializer(serializers.ModelSerializer):
    available_bags = serializers.IntegerField(read_only=True)
    withdrawal_quantity = serializers.IntegerField(read_only=True)
    deposit_date = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Crop
        fields = '__all__'

class WithdrawalSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()