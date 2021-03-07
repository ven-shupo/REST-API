from django.db import models


class Worker(models.Model):
    courier_type = models.CharField(max_length=10)


class Regions(models.Model):
    courier = models.ForeignKey(Worker, on_delete=models.CASCADE)


class Shedule(models.Model):
    courier = models.ForeignKey(Worker, on_delete=models.CASCADE)
    working_hours = models.CharField(max_length=200)
