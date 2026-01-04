from django.db import models
import re


class Order(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Normalize phone number to +91XXXXXXXXXX
        """
        phone = self.phone.strip()

        # Remove all non-digits
        phone_digits = re.sub(r"\D", "", phone)

        # Handle Indian numbers
        if phone_digits.startswith("91") and len(phone_digits) == 12:
            phone_digits = phone_digits[2:]

        if len(phone_digits) == 10:
            self.phone = f"+91{phone_digits}"
        else:
            # fallback (store as-is, but still with +)
            self.phone = f"+{phone_digits}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()