# Generated by Django 3.1.7 on 2021-03-17 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('couriers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courier',
            name='currently_weight',
            field=models.FloatField(default=0),
        ),
    ]