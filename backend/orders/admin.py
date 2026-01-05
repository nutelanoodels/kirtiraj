from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

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
        "whatsapp_link",
        "print_link",
    )
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    def whatsapp_link(self, obj):
        phone = obj.phone.replace("+", "")
        message = f"New Order #{obj.id}"
        url = f"https://wa.me/{phone}?text={message}"
        return format_html('<a href="{}" target="_blank">💬 WhatsApp</a>', url)

    whatsapp_link.short_description = "WhatsApp"

    def print_link(self, obj):
        url = reverse("orders:print", args=[obj.id])
        return format_html('<a href="{}" target="_blank">🖨 Print</a>', url)

    print_link.short_description = "Print"