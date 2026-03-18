from django.shortcuts import get_object_or_404, render
from django.core.mail import send_mail
from django.conf import settings
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
        email=data.get("email"),
        address=data["address"],
        total_amount=0,
    )

    total = 0
    items_summary = []

    for item in data["items"]:
        try:
            product = Product.objects.get(name=item["name"])
            qty = int(item["quantity"])

            OrderItem.objects.create(
                order=order,
                product_name=product.name,
                price=product.price,
                quantity=qty,
            )

            item_total = product.price * qty
            total += item_total
            items_summary.append(f"• {product.name} × {qty} — ₹{item_total}")
        except Product.DoesNotExist:
            continue

    order.total_amount = total
    order.save()

    # Send Emails
    try:
        subject = f"Order Confirmation #{order.id} — Kirtiraj"
        message = f"Hello {order.name},\n\n"
        message += f"Thank you for your order! We have received it and are preparing your fresh, handmade snacks.\n\n"
        message += f"Order ID: #{order.id}\n"
        message += f"Total amount: ₹{order.total_amount}\n\n"
        message += "Items:\n" + "\n".join(items_summary) + "\n\n"
        message += f"Delivery Address:\n{order.address}\n\n"
        message += "We will contact you shortly regarding the delivery.\n\n"
        message += "Best Regards,\nTeam Kirtiraj"

        # 1. Send to Customer
        if order.email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
                fail_silently=True,
            )

        # 2. Send to Owner
        owner_subject = f"NEW ORDER RECEIVED: #{order.id} — {order.name}"
        owner_message = f"You have a new order from {order.name} ({order.phone}).\n\n"
        owner_message += f"Order ID: #{order.id}\n"
        owner_message += f"Customer Email: {order.email or 'N/A'}\n"
        owner_message += f"Address: {order.address}\n\n"
        owner_message += "Order Details:\n" + "\n".join(items_summary) + "\n\n"
        owner_message += f"TOTAL: ₹{order.total_amount}"

        send_mail(
            owner_subject,
            owner_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )
    except Exception as e:
        # We don't want to fail the order if the email fails, but we should log it
        print(f"Email sending failed: {str(e)}")

    return Response({
        "success": True,
        "order_id": order.id
    })


def print_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()

    return render(
        request,
        "orders/print_order.html",
        {
            "order": order,
            "items": items,
        },
    )