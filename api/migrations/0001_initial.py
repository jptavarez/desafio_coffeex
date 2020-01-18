# Generated by Django 3.0.2 on 2020-01-18 16:15

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CoffeeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('shelf_life', models.DateField()),
                ('quantity', models.IntegerField()),
                ('deposit_date', models.DateTimeField(default=datetime.datetime(2020, 1, 18, 13, 15, 8, 24863))),
                ('coffee_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='crops', to='api.CoffeeType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=datetime.datetime(2020, 1, 18, 13, 15, 8, 24863))),
                ('quantity', models.IntegerField()),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawals', to='api.Crop')),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('capacity', models.IntegerField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coffeex_manager', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='crop',
            name='farm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='crops', to='api.Farm'),
        ),
        migrations.AddField(
            model_name='crop',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='crops', to='api.Stock'),
        ),
    ]
