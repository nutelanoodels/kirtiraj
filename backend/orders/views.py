import urllib.parse
import requests
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from products.models import Product
from .models import Order, OrderItem

def send_telegram_message(message):
    """
    Sends a message to the owner's Telegram chat via Bot API.
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    chat_id = getattr(settings, "TELEGRAM_OWNER_CHAT_ID", None)

    if not token or not chat_id:
        print(f"[Telegram] Missing credentials. Logged: {message}")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[Telegram] Alert sent successfully")
            return True
        else:
            print(f"[Telegram] Error: {response.text}")
            return False
    except Exception as e:
        print(f"[Telegram] Exception: {e}")
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

    items_text = "\n".join(items_summary)

    # ── 1. Customer confirmation message ──────────────────────────────────────
    customer_message = (
        f"🧾 *Order Confirmed #{order.id} — Kirtiraj*\n\n"
        f"Hello {order.name},\n\n"
        f"Thank you! We've received your order and are preparing your fresh, "
        f"handmade snacks. 🥨\n\n"
        f"*Order ID:* #{order.id}\n"
        f"*Total:* ₹{order.total_amount}\n\n"
        f"*Items:*\n{items_text}\n\n"
        f"*Delivery Address:*\n{order.address}\n\n"
        f"We'll message you again once it's dispatched! 🙏"
    )

    # Notify Owner via Telegram
    send_telegram_message(owner_message)

    return Response({
        "success": True,
        "order_id": order.id,
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