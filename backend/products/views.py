from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

@api_view(["GET"])
def product_list(request):
    try:
        products = Product.objects.filter(is_available=True)
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