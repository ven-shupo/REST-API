from django.db import models


class Region(models.Model):
    # all regions
    place = models.IntegerField(unique=True)


class Worker(models.Model):

    # ENUM for courier_type
    VEHICLE = [
        ("foot", 'foot'),
        ("bike", 'bike'),
        ("car", 'car'),
        ]

    # feature's worker
    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.CharField(max_length=200, choices=VEHICLE)
    regions = models.ManyToManyField(Region, related_name='couriers')






