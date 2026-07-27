from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from orders.views import admin_dashboard

def root_redirect(request):
    return redirect("/dashboard/")

@staff_member_required(login_url="/admin/login/")
def admin_home_redirect(request):
    return redirect("/dashboard/")

urlpatterns = [
    path("", root_redirect),
    path("admin/", admin_home_redirect),  # Redirect exact /admin/ to dashboard
    path("admin/", admin.site.urls),      # Subpages like login/ and add-products still work
    path("api/", include("products.urls")),
    path("api/orders/", include("orders.urls")),
    # Custom admin dashboard
    path("dashboard/", admin_dashboard, name="dashboard"),
]