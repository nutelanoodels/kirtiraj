from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.conf.urls.static import static


def create_admin(request):
    if User.objects.filter(username="jaymin").exists():
        return HttpResponse("User already exists")

    User.objects.create_superuser(
        username="jaymin",
        email="jaymin@example.com",
        password="lalolalo003"
    )
    return HttpResponse("Superuser jaymin created")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-admin/', create_admin),   # 👈 TEMPORARY
    path('api/', include('products.urls')),
    path("api/orders/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)