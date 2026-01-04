from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "total_amount", "created_at")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    class Media:
        css = {
            "all": ("admin/mobile.css",)
        }