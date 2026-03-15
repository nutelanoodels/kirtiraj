from .views import product_list, health_check

urlpatterns = [
    path("", product_list),
    path("health/", health_check),
]