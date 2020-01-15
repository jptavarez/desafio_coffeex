from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class Withdrawal(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.PROTECT, related_name='withdrawals')
    date = models.DateTimeField(default=datetime.now())
    quatity = models.IntegerField()