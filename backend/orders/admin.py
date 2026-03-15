from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Order, OrderItem
from .utils import build_customer_whatsapp_message

# Custom admin site titles
admin.site.site_header = "Kirtiraj Orders"
admin.site.site_title = "Kirtiraj Admin"
admin.site.index_title = "Order Management"


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
        "status",
        "created_at",
        "whatsapp_link",
        "print_link",
    )
    list_filter = ("status", "created_at")
    search_fields = ("name", "phone", "address")
    list_editable = ("status",)
    ordering = ("-created_at",)

    inlines = [OrderItemInline]

    def whatsapp_link(self, obj):
        try:
            message = build_customer_whatsapp_message(obj)
            phone = obj.phone.replace("+", "")
            url = f"https://wa.me/{phone}?text={message}"
            return format_html('<a href="{}" target="_blank">💬 WhatsApp</a>', url)
        except Exception:
            return "—"

    whatsapp_link.short_description = "WhatsApp"

    def print_link(self, obj):
        try:
            url = reverse("orders:print", args=[obj.id])
            return format_html('<a href="{}" target="_blank">🖨 Print</a>', url)
        except Exception:
            return "—"

    print_link.short_description = "Print"