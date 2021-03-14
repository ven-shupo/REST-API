from django.contrib import admin
from .models import Order, Order_to_Worker, Complete_Order, Delivery_time

admin.site.register(Order)
admin.site.register(Order_to_Worker)
admin.site.register(Delivery_time)
admin.site.register(Complete_Order)