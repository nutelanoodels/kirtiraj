from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "total_amount", "print_link")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    def print_link(self, obj):
        return format_html(
            '<a href="/api/orders/{}/print/" target="_blank">🖨 Print</a>',
            obj.id
        )

    print_link.short_description = "Print"

    class Media:
        css = {
            "all": ("admin/mobile.css",)
        }