from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderItem


@api_view(["POST"])
def create_order(request):
    data = request.data

    order = Order.objects.create(
        name=data["name"],
        phone=data["phone"],
        address=data["address"],
        total_amount=data["total_amount"],
    )

    for item in data["items"]:
        OrderItem.objects.create(
            order=order,
            product_name=item["name"],
            price=item["rate"],
            quantity=item["quantity"],
        )

    return Response({"success": True, "order_id": order.id})


def print_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "print_order.html", {"order": order})