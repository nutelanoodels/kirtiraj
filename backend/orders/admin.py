from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Order, OrderItem

try:
    from .utils import build_whatsapp_message
except Exception:
    build_whatsapp_message = None


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
        "whatsapp_link",
        "print_link",
    )
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    def whatsapp_link(self, obj):
        if not build_whatsapp_message:
            return "WhatsApp error"

        try:
            message = build_whatsapp_message(obj)
            phone = obj.phone.replace("+", "")
            url = f"https://wa.me/{phone}?text={message}"
            return format_html('<a href="{}" target="_blank">💬 WhatsApp</a>', url)
        except Exception as e:
            return f"Error"

    whatsapp_link.short_description = "WhatsApp"

    def print_link(self, obj):
        try:
            url = reverse("orders:print", args=[obj.id])
            return format_html('<a href="{}" target="_blank">🖨 Print</a>', url)
        except Exception:
            return "Print error"

    class Media:
        css = {"all": ("admin/mobile.css",)}