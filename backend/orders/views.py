import re
import json
import urllib.parse
import requests
from datetime import date, timedelta, datetime

from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response

from products.models import Product
from .models import Order, OrderItem
from .utils import build_customer_whatsapp_message


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

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


def _normalize_phone(raw):
    """Normalize a phone string to +91XXXXXXXXXX format."""
    digits = re.sub(r"\D", "", raw.strip())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) == 10:
        return f"+91{digits}"
    return f"+{digits}"


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

@api_view(["POST"])
def create_order(request):
    try:
        data = request.data
        print(f"[Debug] Received order request: {data}")

        delivery_option = data.get("delivery_option")
        valid_delivery_options = {choice[0] for choice in Order.DELIVERY_OPTION_CHOICES}
        if delivery_option not in valid_delivery_options:
            return Response({"success": False, "error": "A valid delivery option is required."}, status=400)

        order = Order.objects.create(
            name=data["name"],
            phone=data["phone"],
            email=data.get("email"),
            address=data["address"],
            delivery_option=delivery_option,
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
                print(f"[Debug] Product not found: {item.get('name')}")
                continue

        order.total_amount = total
        if delivery_option == "home_delivery" and total < 500:
            order.delete()
            return Response({"success": False, "error": "Home delivery requires a minimum order of ₹500."}, status=400)
        order.save()

        items_text = "\n".join(items_summary)

        # ── 1. Customer confirmation message (Construct text only) ──
        customer_message = (
            f"🧾 *Order Confirmed #{order.id} — Kirtiraj*\n\n"
            f"Hello {order.name},\n\n"
            f"Thank you! We've received your order and are preparing your fresh, "
            f"snacks. 🥨\n\n"
            f"*Order ID:* #{order.id}\n"
            f"*Summary:* \n"
            f"Total items: {len(data['items'])}\n"
            f"Total quantity: {sum(int(item['quantity']) for item in data['items'])}\n\n"
            f"*Total:* ₹{order.total_amount}\n\n"
            f"*Delivery option:* {order.get_delivery_option_display()}\n\n"
            f"*Items:*\n{items_text}\n\n"
            f"*Delivery Address:*\n{order.address}\n\n"
            f"We'll message you again once it's dispatched! 🙏"
        )

        # ── 2. Owner order summary message ──
        owner_message = (
            f"🔔 *NEW ORDER — Kirtiraj*\n\n"
            f"👤 *Customer:* {order.name}\n"
            f"📞 *Phone:* {order.phone}\n"
            f"🆔 *Order ID:* #{order.id}\n\n"
            f"🚚 *Delivery option:* {order.get_delivery_option_display()}\n\n"
            f"🛒 *Items:*\n{items_text}\n\n"
            f"📦 *Delivery Address:*\n{order.address}\n\n"
            f"📊 *Stats:*\n"
            f"Total items: {len(data['items'])}\n"
            f"Total quantity: {sum(int(item['quantity']) for item in data['items'])}\n\n"
            f"💰 *TOTAL: ₹{order.total_amount}*"
        )

        # Notify Owner via Telegram
        send_telegram_message(owner_message)

        return Response({
            "success": True,
            "order_id": order.id,
        })
    except Exception as e:
        import traceback
        print(f"[Error] Failed to create order: {e}")
        traceback.print_exc()
        return Response({
            "success": False,
            "error": str(e)
        }, status=500)


@api_view(["GET"])
def customer_lookup(request):
    """
    Given ?phone=<number>, return the most recent order's name, address,
    and delivery_option for that customer. Used for checkout autofill.
    """
    raw = request.GET.get("phone", "").strip()
    if not raw:
        return Response({"found": False})

    normalized = _normalize_phone(raw)
    order = Order.objects.filter(phone=normalized).order_by("-created_at").first()
    if not order:
        return Response({"found": False})

    return Response({
        "found": True,
        "name": order.name,
        "address": order.address,
        "delivery_option": order.delivery_option,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Print view (existing)
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# Admin Dashboard views  (protected — must be logged-in staff)
# ─────────────────────────────────────────────────────────────────────────────

@staff_member_required(login_url="/admin/login/")
def admin_dashboard(request):
    """Render the custom admin dashboard HTML page."""
    return render(request, "orders/dashboard.html")


@staff_member_required(login_url="/admin/login/")
def admin_orders_api(request):
    """
    JSON API returning orders filtered by query params.
    Params: filter (today|week|month|date|all), date, status, search
    """
    qs = Order.objects.prefetch_related("items").order_by("-created_at")

    # ── Time filter ──
    f = request.GET.get("filter", "all")
    today_local = timezone.localdate()

    if f == "today":
        qs = qs.filter(created_at__date=today_local)
    elif f == "week":
        week_ago = today_local - timedelta(days=6)
        qs = qs.filter(created_at__date__gte=week_ago)
    elif f == "month":
        qs = qs.filter(
            created_at__year=today_local.year,
            created_at__month=today_local.month,
        )
    elif f == "date":
        raw_date = request.GET.get("date", "")
        try:
            d = date.fromisoformat(raw_date)
            qs = qs.filter(created_at__date=d)
        except ValueError:
            pass

    # ── Status filter ──
    status = request.GET.get("status", "")
    if status in ("pending", "dispatched", "delivered"):
        qs = qs.filter(status=status)

    # ── Search ──
    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(phone__icontains=search)
            | Q(address__icontains=search)
        )

    orders_data = []
    for o in qs:
        items_list = [
            {"name": i.product_name, "qty": i.quantity, "price": float(i.price)}
            for i in o.items.all()
        ]
        # WhatsApp link
        try:
            wa_msg = build_customer_whatsapp_message(o)
            phone_digits = o.phone.replace("+", "")
            wa_url = f"https://wa.me/{phone_digits}?text={wa_msg}"
        except Exception:
            wa_url = ""

        orders_data.append({
            "id": o.id,
            "name": o.name,
            "phone": o.phone,
            "address": o.address,
            "delivery_option": o.get_delivery_option_display(),
            "delivery_option_key": o.delivery_option,
            "total_amount": float(o.total_amount),
            "status": o.status,
            "created_at": timezone.localtime(o.created_at).strftime("%d %b %Y, %I:%M %p"),
            "items": items_list,
            "wa_url": wa_url,
        })

    return JsonResponse({"orders": orders_data, "count": len(orders_data)})


@staff_member_required(login_url="/admin/login/")
def admin_stats_api(request):
    """
    JSON API returning dashboard stats:
    - today / week / month order count + revenue
    - top 10 selling products
    - top 10 frequent customers
    - counts by status
    """
    today_local = timezone.localdate()
    week_ago = today_local - timedelta(days=6)

    def _rev(qs):
        return float(qs.aggregate(r=Sum("total_amount"))["r"] or 0)

    all_orders = Order.objects.all()
    today_orders = all_orders.filter(created_at__date=today_local)
    week_orders = all_orders.filter(created_at__date__gte=week_ago)
    month_orders = all_orders.filter(
        created_at__year=today_local.year,
        created_at__month=today_local.month,
    )

    # Top products by total quantity sold
    top_products = (
        OrderItem.objects.values("product_name")
        .annotate(total_qty=Sum("quantity"), total_rev=Sum("price"))
        .order_by("-total_qty")[:10]
    )

    # Top customers by order count
    top_customers = (
        Order.objects.values("name", "phone")
        .annotate(order_count=Count("id"), total_spent=Sum("total_amount"))
        .order_by("-order_count")[:10]
    )

    # Status counts
    pending_count = all_orders.filter(status="pending").count()
    dispatched_count = all_orders.filter(status="dispatched").count()
    delivered_count = all_orders.filter(status="delivered").count()

    return JsonResponse({
        "today": {"count": today_orders.count(), "revenue": _rev(today_orders)},
        "week": {"count": week_orders.count(), "revenue": _rev(week_orders)},
        "month": {"count": month_orders.count(), "revenue": _rev(month_orders)},
        "all": {"count": all_orders.count(), "revenue": _rev(all_orders)},
        "status": {
            "pending": pending_count,
            "dispatched": dispatched_count,
            "delivered": delivered_count,
        },
        "top_products": list(top_products),
        "top_customers": [
            {
                "name": c["name"],
                "phone": c["phone"],
                "order_count": c["order_count"],
                "total_spent": float(c["total_spent"] or 0),
            }
            for c in top_customers
        ],
    })


@staff_member_required(login_url="/admin/login/")
@csrf_exempt
def admin_update_status(request, order_id):
    """POST with {status: 'pending'|'dispatched'|'delivered'} to update order status."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    order = get_object_or_404(Order, id=order_id)
    try:
        body = json.loads(request.body)
        new_status = body.get("status", "")
    except Exception:
        new_status = request.POST.get("status", "")

    valid = {c[0] for c in Order.STATUS_CHOICES}
    if new_status not in valid:
        return JsonResponse({"error": "Invalid status"}, status=400)

    # ── Enforce status lifecycle: once changed, it cannot go back ──
    # Valid flow: pending -> dispatched -> delivered
    if order.status == "delivered":
        return JsonResponse({"error": "This order is already delivered and completed. Status cannot be changed."}, status=400)

    if order.status == "dispatched":
        if new_status == "pending":
            return JsonResponse({"error": "This order has already been dispatched. Cannot set back to pending."}, status=400)

    order.status = new_status
    order.save(update_fields=["status"])
    return JsonResponse({"success": True, "status": order.status})

