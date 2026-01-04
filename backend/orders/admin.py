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
        "print_button",
    )
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    def print_button(self, obj):
        url = reverse("print_order", args=[obj.id])
        return format_html(
            '<a class="button" href="{}" target="_blank">🖨 Print</a>',
            url
        )

    print_button.short_description = "Print"

    class Media:
        css = {
            "all": ("admin/mobile.css",)
        }