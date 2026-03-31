from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "name", "category", "size_display", "price", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name",)
    list_editable = ("price", "is_available")
    ordering = ("category", "name")
    actions = ["mark_available", "mark_unavailable"]

    def image_preview(self, obj):
        try:
            if obj.image:
                return format_html(
                    '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />',
                    obj.image,
                )
        except Exception:
            return "—"
        return "—"
    image_preview.short_description = "Image"

    def size_display(self, obj):
        if obj.size is None:
            return "—"
        grams = int(obj.size * 1000)
        if grams >= 1000:
            return f"{obj.size:g} kg"
        return f"{grams} g"
    size_display.short_description = "Size"
    size_display.admin_order_field = "size"

    @admin.action(description="✅ Mark selected products as Available")
    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f"{updated} product(s) marked as available.")

    @admin.action(description="❌ Mark selected products as Unavailable (Out of Stock)")
    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f"{updated} product(s) marked as unavailable.")