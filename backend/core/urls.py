from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from orders.views import admin_dashboard

def root_redirect(request):
    return redirect("/admin/")

urlpatterns = [
    path("", root_redirect),
    path("admin/", admin.site.urls),
    path("api/", include("products.urls")),
    path("api/orders/", include("orders.urls")),
    # Custom admin dashboard
    path("dashboard/", admin_dashboard, name="dashboard"),
]