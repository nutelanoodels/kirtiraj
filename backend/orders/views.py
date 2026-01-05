from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

@csrf_exempt
@api_view(["POST"])
def create_order(request):
    data = request.data

    # basic validation
    if not data.get("name") or not data.get("phone") or not data.get("items"):
        return Response({"detail": "Invalid data"}, status=400)

    order = Order.objects.create(
        name=data["name"],
        phone=data["phone"],
        address=data.get("address", ""),
        total_amount=0,  # frontend must NOT control this
    )

    for item in data["items"]:
        OrderItem.objects.create(
            order=order,
            product_name=item["name"],
            price=0,        # do NOT trust frontend price
            quantity=item["quantity"],
        )

    return Response({
        "success": True,
        "order_id": order.id
    })