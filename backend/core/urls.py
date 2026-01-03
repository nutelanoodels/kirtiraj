# core/urls.py
from django.contrib.auth.models import User
from django.http import HttpResponse

def bootstrap_admin(request):
    if User.objects.filter(username="jaymin").exists():
        return HttpResponse("Admin already exists")

    User.objects.create_superuser(
        username="jaymin",
        email="jaymin@example.com",
        password="lalolalo003"
    )
    return HttpResponse("Admin created successfully")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bootstrap-admin/", bootstrap_admin),
    path("api/", include("products.urls")),
    path("api/orders/", include("orders.urls")),
]