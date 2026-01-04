from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import localtime

from .models import Order, OrderItem


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "total_amount",
        "created_at",
        "print_link",
        "whatsapp_link",
    )
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    class Media:
        css = {
            "all": ("admin/mobile.css",)
        }

    # 🖨 PRINT
    def print_link(self, obj):
        url = reverse("orders:print", args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank">🖨 Print</a>',
            url
        )

    print_link.short_description = "Print"

    # 🟢 WHATSAPP
    def whatsapp_link(self, obj):
        items = []
        for item in obj.orderitem_set.all():
            items.append(
                f"- {item.product_name} x {item.quantity} = ₹{item.price * item.quantity}"
            )

        items_text = "%0A".join(items)

        order_time = localtime(obj.created_at).strftime("%d %b %Y, %I:%M %p")

        message = (
            f"Hello {obj.name},%0A%0A"
            f"🧾 *Order Confirmation*%0A"
            f"Order ID: {obj.id}%0A"
            f"Date: {order_time}%0A%0A"
            f"*Items:*%0A{items_text}%0A%0A"
            f"*Total:* ₹{obj.total_amount}%0A%0A"
            f"Thank you for ordering from Kirtiraj 🙏"
        )

        phone = obj.phone.replace(" ", "").replace("+", "")
        url = f"https://wa.me/{phone}?text={message}"

        return format_html(
            '<a href="{}" target="_blank">🟢 WhatsApp</a>',
            url
        )

    whatsapp_link.short_description = "WhatsApp"