from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product

@api_view(["GET"])
def product_list(request):
    products = Product.objects.select_related("category")
    data = []

    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category": p.category.name,
            "image": p.image.url if p.image else None,
        })

    return Response(data)