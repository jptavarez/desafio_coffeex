from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coffeex_manager = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Stock(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    @property
    def available_bags(self):
        crops = self.crops.all()
        available = 0
        for crop in crops:
            available += crop.available_bags
        return available
    
    @property
    def withdrawal_quantity(self):
        crops = self.crops.all()
        withdrawals = 0
        for crop in crops:
            withdrawals += crop.withdrawal_quantity
        return withdrawals
    
    @property
    def coffee_types(self):
        return [crop.coffee_type for crop in self.crops.all()]
    
    @property
    def origin_farms(self):
        return [crop.farm for crop in self.crops.all()]


class CoffeeType(models.Model):
    name = models.CharField(max_length=100)

class Farm(models.Model):
    name = models.CharField(max_length=100)

class Crop(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name='crops')
    coffee_type = models.ForeignKey(CoffeeType, on_delete=models.PROTECT, related_name='crops') 
    farm = models.ForeignKey(Farm, on_delete=models.PROTECT, related_name='crops') 
    shelf_life = models.DateField()
    quantity = models.IntegerField()
    deposit_date = models.DateTimeField(default=datetime.now())

    @property
    def withdrawal_quantity(self):
        withdrawals = self.withdrawals.aggregate(Sum('quatity'))['quatity__sum']
        return withdrawals if withdrawals else 0
    
    @property
    def available_bags(self):   
        return self.quantity - self.withdrawal_quantity
    
    def withdrawal(self, quantity, user):
        withdrawal = Withdrawal(crop=self, quatity=quantity)
        withdrawal.save()
    
    def user_authorized(self, user: User):
        if not user.profile.coffeex_manager and self.stock.owner != user:
            return False 
        return True

class Withdrawal(models.Model):    
    crop = models.ForeignKey(Crop, on_delete=models.PROTECT, related_name='withdrawals')
    date = models.DateTimeField(default=datetime.now())
    quatity = models.IntegerField() # todo: fix typo