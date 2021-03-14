from django.conf.urls import url
from . import views

urlpatterns = [
    url('$', views.post_couriers),
    url(r'/(\d+)$', views.edit_courier)
]
