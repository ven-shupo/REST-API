# Generated by Django 3.1.7 on 2021-03-20 09:16

from django.db import migrations, models
import django.db.models.deletion
import orders.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('couriers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.IntegerField(primary_key=True, serialize=False, validators=[orders.models.validator_id])),
                ('weight', models.FloatField(validators=[orders.models.validator_weight])),
                ('region', models.IntegerField(validators=[orders.models.validator_id])),
            ],
        ),
        migrations.CreateModel(
            name='Order_to_Courier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_order', models.DateTimeField(blank=True)),
                ('courier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='couriers.courier')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
            ],
        ),
        migrations.CreateModel(
            name='Delivery_time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.TimeField()),
                ('end', models.TimeField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
            ],
        ),
        migrations.CreateModel(
            name='Complete_Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_assign', models.DateTimeField(blank=True)),
                ('time_complete', models.DateTimeField(blank=True)),
                ('region', models.IntegerField()),
                ('c', models.IntegerField()),
                ('courier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='couriers.courier')),
            ],
        ),
    ]
