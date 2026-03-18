from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "price", "category", "image"]

    def get_category(self, obj):
        return obj.category.name if obj.category else "Others"