import urllib.parse
import requests
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from products.models import Product
from .models import Order, OrderItem

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"


def send_callmebot(phone, message, apikey):
    """
    Sends a WhatsApp message using CallMeBot (free service).
    The recipient must have registered their number with CallMeBot first.
    See: https://www.callmebot.com/blog/free-api-whatsapp-messages/

    phone   — international format without '+', e.g. '919173760611'
    message — plain text (emoji supported)
    apikey  — the personal API key CallMeBot assigned to that phone number
    """
    if not apikey:
        print(f"[CallMeBot] No API key provided. Logging message for {phone}:\n{message}")
        return False

    try:
        params = {
            "phone": phone,
            "text": message,
            "apikey": apikey,
        }
        url = f"{CALLMEBOT_URL}?{urllib.parse.urlencode(params)}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"[CallMeBot] Message sent to {phone}")
            return True
        else:
            print(f"[CallMeBot] Failed for {phone}: {response.status_code} — {response.text}")
            return False
    except Exception as e:
        print(f"[CallMeBot] Exception while sending to {phone}: {e}")
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

    # Customer must have registered their number with CallMeBot.
    # CALLMEBOT_CUSTOMER_API_KEY is optional — fails silently if absent.
    customer_apikey = getattr(settings, "CALLMEBOT_CUSTOMER_API_KEY", None)
    customer_phone = order.phone.replace("+", "").replace(" ", "")
    send_callmebot(customer_phone, customer_message, customer_apikey)

    # ── 2. Owner order summary message ────────────────────────────────────────
    owner_message = (
        f"🔔 *NEW ORDER — Kirtiraj*\n\n"
        f"👤 *Customer:* {order.name}\n"
        f"📞 *Phone:* {order.phone}\n"
        f"🆔 *Order ID:* #{order.id}\n\n"
        f"🛒 *Items:*\n{items_text}\n\n"
        f"📦 *Delivery Address:*\n{order.address}\n\n"
        f"💰 *TOTAL: ₹{order.total_amount}*"
    )

    owner_phone = getattr(settings, "ADMIN_PHONE", "919173760611")
    owner_apikey = getattr(settings, "CALLMEBOT_OWNER_API_KEY", None)
    send_callmebot(owner_phone, owner_message, owner_apikey)

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