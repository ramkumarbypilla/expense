from django.db import models

class Ride(models.Model):
    ride_from = models.CharField(max_length=100)
    ride_to = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=20)
    ride_type = models.CharField(max_length=20, default='app')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    tips = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ride_from} -> {self.ride_to} ({self.payment_type})"

