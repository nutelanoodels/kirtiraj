from django.contrib import admin
from .models import Order, OrderItem
from django.utils.html import format_html

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "total_amount", "print_pdf", "created_at")
    inlines = [OrderItemInline]

    def print_pdf(self, obj):
        return format_html(
            '<a href="/api/orders/{}/print/" target="_blank">Print PDF</a>',
            obj.id
        )

    print_pdf.short_description = "Print"
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