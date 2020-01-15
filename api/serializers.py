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

# class StockSerializer(serializers.ModelSerializer):
#     coffee_types = CoffeeTypeSerializer(source='crops.get.coffee_type', many=True)
#     origin_farms = FarmSerializer(source='crops.get.farm', many=True)
#     class Meta:
#         model = Stock
#         fields = '__all__'
#         extra_kwargs = {'owner': {'default': serializers.CurrentUserDefault()}}