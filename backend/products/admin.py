from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "name", "price", "category", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name",)
    list_editable = ("price", "is_available")

    def image_preview(self, obj):
        try:
            if obj.image:
                return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />', obj.image.url)
        except Exception:
            return "Error loading image"
        return "No Image"
    
    image_preview.short_description = "Preview"