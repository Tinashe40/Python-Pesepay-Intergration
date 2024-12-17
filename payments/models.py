from django.db import models
import uuid


class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Payment {self.payment_id}"


class Donation(models.Model):
    id = models.AutoField(primary_key=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='donation')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency_code = models.CharField(max_length=10)
    payment_reason = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='Pending')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation {self.id} - {self.status}"
