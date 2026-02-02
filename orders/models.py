from django.db import models
from django.conf import settings
from boutique.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('paid', 'Payée'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('stripe', 'Carte bancaire'),
        ('mobile', 'Mobile Money'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('failed', 'Échoué'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='stripe'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

