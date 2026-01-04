from django.contrib import admin
from .models import Order, OrderItem
from django.utils.html import format_html
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

def print_order(self, obj):
    return format_html(
        '<a href="/admin/orders/order/{}/print/" target="_blank">🖨 Print</a>',
        obj.id
    )

print_order.short_description = "Print"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "total_amount", "print_order")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    class Media:
        css = {
            "all": ("admin/mobile.css",)
        }
