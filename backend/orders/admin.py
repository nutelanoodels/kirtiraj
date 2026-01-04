from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "total_amount", "created_at")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]

    class Media:
        css = {
            "all": ("admin/mobile.css",)
        }