from django.urls import path
from .views import create_order
from django.urls import path
from .views import print_order

urlpatterns = [
    path("<int:order_id>/print/", print_order),
]
urlpatterns = [
    path("create/", create_order),
]