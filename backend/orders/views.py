from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from products.models import Product
from .models import Order, OrderItem


@api_view(["POST"])
def create_order(request):
    data = request.data

    order = Order.objects.create(
        name=data["name"],
        phone=data["phone"],
        address=data["address"],
        total_amount=0,
    )

    total = 0

    for item in data["items"]:
        product = Product.objects.get(name=item["name"])
        qty = item["quantity"]

        OrderItem.objects.create(
            order=order,
            product_name=product.name,
            price=product.price,
            quantity=qty,
        )

        total += product.price * qty

    order.total_amount = total
    order.save()

    return Response({
        "success": True,
        "order_id": order.id
    })


def print_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/print_order.html", {"order": order})