from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, OrderItem
from django.shortcuts import get_object_or_404, render
from .models import Order
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from .models import Order
@api_view(["POST"])
def print_order(request, order_id):
    order = Order.objects.get(id=order_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="order_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, f"Order #{order.id}")
    y -= 30

    p.setFont("Helvetica", 11)
    p.drawString(40, y, f"Name: {order.name}")
    y -= 18
    p.drawString(40, y, f"Phone: {order.phone}")
    y -= 18
    p.drawString(40, y, f"Address: {order.address}")
    y -= 25

    p.drawString(40, y, "Items:")
    y -= 20

    for item in order.items.all():
        p.drawString(
            50,
            y,
            f"- {item.product_name} × {item.quantity} = ₹{item.price}"
        )
        y -= 15

        if y < 50:
            p.showPage()
            y = height - 40

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, f"Total: ₹{order.total_amount}")

    p.showPage()
    p.save()
    return response

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