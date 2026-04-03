from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Case, When, Value, BooleanField, Q
from .models import Product
from .serializers import ProductSerializer

@api_view(["GET"])
def product_list(request):
    try:
        products = Product.objects.filter(is_available=True).annotate(
            has_image=Case(
                When(~Q(image=None) & ~Q(image=""), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).order_by("-has_image", "name")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            "error": "Database connection failed",
            "detail": str(e)
        }, status=500)

@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok", "message": "Server is running"})