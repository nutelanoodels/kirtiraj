import requests
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from products.models import Product
from .models import Order, OrderItem


def send_whatsapp(phone, message):
    """
    Sends a WhatsApp message using a third-party API (e.g., UltraMsg).
    Configurable via environment variables.
    """
    api_url = getattr(settings, "WHATSAPP_API_URL", None)
    api_token = getattr(settings, "WHATSAPP_API_TOKEN", None)
    instance_id = getattr(settings, "WHATSAPP_INSTANCE_ID", None)

    if not api_url or not api_token:
        print("WhatsApp API not configured. Logging message instead:")
        print(f"TO: {phone}\nMSG: {message}")
        return False

    # Example for UltraMsg style API
    # You can swap this for Twilio or any other provider
    try:
        payload = {
            "token": api_token,
            "to": phone,
            "body": message,
        }
        # UltraMsg usually needs the instance_id in the URL
        url = api_url.format(instance_id=instance_id) if instance_id else api_url
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"WhatsApp sending failed: {str(e)}")
        return False


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

    # Construct Message
    message = f"🧾 *Order Confirmation #{order.id} — Kirtiraj*\n\n"
    message += f"Hello {order.name},\n\n"
    message += f"Thank you! We've received your order and are preparing your fresh, handmade snacks. 🥨\n\n"
    message += f"Order ID: #{order.id}\n"
    message += f"Total: ₹{order.total_amount}\n\n"
    message += "*Items:*\n" + "\n".join(items_summary) + "\n\n"
    message += f"*Delivery Address:*\n{order.address}\n\n"
    message += "We'll message you again once it's dispatched! 🙏"

    # 1. Send to Customer
    send_whatsapp(order.phone, message)

    # 2. Send to Owner (Admin Alerts)
    admin_phone = getattr(settings, "ADMIN_PHONE", "919173760611")
    owner_message = f"🔔 *NEW ORDER RECEIVED*\n\n"
    owner_message += f"From: {order.name}\n"
    owner_message += f"Phone: {order.phone}\n"
    owner_message += f"Order ID: #{order.id}\n\n"
    owner_message += "*Items:*\n" + "\n".join(items_summary) + "\n\n"
    owner_message += f"*TOTAL: ₹{order.total_amount}*"

    send_whatsapp(admin_phone, owner_message)

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