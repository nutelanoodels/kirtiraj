from django.db import models
import re


class Order(models.Model):
    DELIVERY_OPTION_CHOICES = [
        ("home_delivery", "Home delivery (within 10 km of Gota; free; minimum order ₹7,500)"),
        ("porter", "Porter (within Ahmedabad; chargeable)"),
        ("courier", "Courier (within India; chargeable)"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("dispatched", "Dispatched"),
        ("delivered", "Delivered"),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField()
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_OPTION_CHOICES, default="porter")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        phone = self.phone.strip()
        digits = re.sub(r"\D", "", phone)

        if digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]

        if len(digits) == 10:
            self.phone = f"+91{digits}"
        else:
            self.phone = f"+{digits}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} — {self.name} [{self.get_status_display()}]"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
