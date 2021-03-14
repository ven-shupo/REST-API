from django.contrib import admin
from .models import Schedule, Worker, Region

admin.site.register(Schedule)
admin.site.register(Worker)
admin.site.register(Region)