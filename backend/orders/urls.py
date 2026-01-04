from django.urls import path
from .views import create_order, print_order

app_name = "orders"

urlpatterns = [
    path("create/", create_order, name="create"),
    path("<int:order_id>/print/", print_order, name="print"),
]