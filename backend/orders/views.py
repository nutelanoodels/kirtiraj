from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, OrderItem
from django.shortcuts import get_object_or_404, render
from .models import Order


@api_view(["POST"])
def print_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/print.html", {"order": order})
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