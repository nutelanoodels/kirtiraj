from django.urls import path
from .views import (
    create_order,
    print_order,
    customer_lookup,
    admin_dashboard,
    admin_orders_api,
    admin_stats_api,
    admin_update_status,
)

app_name = "orders"

urlpatterns = [
    # Public API
    path("create/", create_order, name="create"),
    path("customer-lookup/", customer_lookup, name="customer_lookup"),

    # Print bill
    path("print/<int:order_id>/", print_order, name="print"),

    # Admin dashboard JSON APIs  (called from dashboard.html via fetch)
    path("admin-api/orders/", admin_orders_api, name="admin_orders_api"),
    path("admin-api/stats/", admin_stats_api, name="admin_stats_api"),
    path("admin-api/orders/<int:order_id>/status/", admin_update_status, name="admin_update_status"),
]