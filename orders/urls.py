from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.post_orders),
    url('^/assign$', views.assign),
    url('^/complete$', views.complete)
]
