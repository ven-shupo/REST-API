from django.db import models
from django.core.exceptions import ValidationError


def checker(value):
    if value <= 0:
        raise ValidationError(message='%s is negative' % value)
    if not isinstance(value, int):
        raise ValidationError(message='%s is not an integer' % value)


class Region(models.Model):
    # all regions
    place = models.IntegerField(unique=True, validators=[checker])


class Worker(models.Model):

    # ENUM for courier_type
    VEHICLE = [
        ("foot", 'foot'),
        ("bike", 'bike'),
        ("car", 'car'),
        ]

    # feature's worker
    courier_id = models.IntegerField(primary_key=True, validators=[checker])
    courier_type = models.CharField(max_length=200, choices=VEHICLE)
    regions = models.ManyToManyField(Region, related_name='couriers')


class Schedule(models.Model):
    # Schedule workers
    courier = models.ForeignKey(Worker, on_delete=models.CASCADE)
    begin = models.TimeField()
    end = models.TimeField()