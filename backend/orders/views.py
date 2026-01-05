from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal

@api_view(["POST"])
def create_order(request):
    data = request.data

    items = data.get("items", [])

    if not items:
        return Response({"detail": "No items provided"}, status=400)

    # ✅ Calculate total safely on backend
    total_amount = Decimal("0.00")

    order = Order.objects.create(
        name=data["name"],
        phone=data["phone"],
        address=data["address"],
        total_amount=0,  # temporary
    )

    for item in items:
        # ⚠️ TEMP: price = 0 (since you're not charging online yet)
        price = Decimal("0.00")

        OrderItem.objects.create(
            order=order,
            product_name=item["name"],
            price=price,
            quantity=item["quantity"],
        )

        total_amount += price * item["quantity"]

    order.total_amount = total_amount
    order.save()

    return Response({
        "success": True,
        "order_id": order.id
    })