from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem


@api_view(["POST"])
def create_order(request):
    data = request.data

    # 🔴 Defensive checks (avoid 500s)
    required_fields = ["name", "phone", "address", "items"]
    for field in required_fields:
        if field not in data:
            return Response(
                {"success": False, "detail": f"Missing field: {field}"},
                status=400
            )

    order = Order.objects.create(
        name=data["name"],
        phone=data["phone"],
        address=data["address"],
        total_amount=0,  # calculated later if needed
    )

    total = 0

    for item in data["items"]:
        price = item.get("rate", 0)
        qty = item.get("quantity", 1)

        OrderItem.objects.create(
            order=order,
            product_name=item["name"],
            price=price,
            quantity=qty,
        )

        total += price * qty

    order.total_amount = total
    order.save()

    return Response({
        "success": True,
        "order_id": order.id
    })


def print_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(
        request,
        "orders/print_order.html",
        {"order": order}
    )