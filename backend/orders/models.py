from django.db import models
import re


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("dispatched", "Dispatched"),
        ("delivered", "Delivered"),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField()
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