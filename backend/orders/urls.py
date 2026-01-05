from django.urls import path
from .views import create_order, print_order

urlpatterns = [
    path("create/", create_order, name="create-order"),
    path("print/<int:order_id>/", print_order, name="print-order"),
]