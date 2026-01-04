from django.urls import path
from .views import create_order, print_order

urlpatterns = [
    path("create/", create_order),
    path("<int:order_id>/print/", print_order),
]