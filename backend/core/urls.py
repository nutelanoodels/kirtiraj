from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth.models import User





urlpatterns = [
    path("admin/", admin.site.urls),
    
    path("api/", include("products.urls")),
    path("api/orders/", include("orders.urls")),
]