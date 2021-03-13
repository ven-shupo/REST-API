from django.db import models
from django.core.exceptions import ValidationError
from couriers.models import Worker


def validator_id(value):
    if value <= 0:
        raise ValidationError(message='%s is negative' % value)
    if not isinstance(value, int):
        raise ValidationError(message='%s is not an integer' % value)


def validator_weight(value):
    if value < 0.01 or value > 50:
        raise ValidationError(message='%s weight is not valid' % value)
    if not isinstance(value, (int, float)):
        raise ValidationError(message='%s weight is not an float' % value)


class Order(models.Model):
    # feature's order
    order_id = models.IntegerField(primary_key=True, validators=[validator_id])
    weight = models.FloatField(validators=[validator_weight])
    region = models.IntegerField(validators=[validator_id])


class Delivery_time(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    begin = models.TimeField()
    end = models.TimeField()


class Order_to_Worker(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    courier = models.ForeignKey(Worker, on_delete=models.PROTECT)
    time_order = models.DateTimeField(blank=True)


class Complete_Order(models.Model):
    courier = models.ForeignKey(Worker, on_delete=models.PROTECT)
    time_assign = models.DateTimeField(blank=True)
    time_complete = models.DateTimeField(blank=True)







