# Generated by Django 3.1.7 on 2021-03-18 20:00

import couriers.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('courier_id', models.IntegerField(primary_key=True, serialize=False, validators=[couriers.models.checker])),
                ('courier_type', models.CharField(choices=[('foot', 'foot'), ('bike', 'bike'), ('car', 'car')], max_length=200)),
                ('currently_weight', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.IntegerField(unique=True, validators=[couriers.models.checker])),
            ],
        ),
        migrations.CreateModel(
            name='Working_hours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.TimeField()),
                ('end', models.TimeField()),
                ('courier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='couriers.courier')),
            ],
        ),
        migrations.AddField(
            model_name='courier',
            name='regions',
            field=models.ManyToManyField(related_name='couriers', to='couriers.Region'),
        ),
    ]
