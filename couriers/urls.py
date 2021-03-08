from django.conf.urls import url
from django.urls import path
from . import views


urlpatterns = [
    url('^$', views.post_couriers),
    url('(\d+)/$', views.edit_courier)
]
