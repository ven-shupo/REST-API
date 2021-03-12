from django.conf.urls import url
from . import views

urlpatterns = [
    url('$', views.post_orders),
    # url('/(\d+)$', views.edit_courier)
]
