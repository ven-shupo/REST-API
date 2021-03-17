from django.contrib import admin
from .models import Order, Order_to_Courier, Complete_Order, Delivery_time

admin.site.register(Order)
admin.site.register(Order_to_Courier)
admin.site.register(Delivery_time)
admin.site.register(Complete_Order)