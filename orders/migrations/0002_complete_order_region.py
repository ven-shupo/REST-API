# Generated by Django 3.1.7 on 2021-03-18 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='complete_order',
            name='region',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
