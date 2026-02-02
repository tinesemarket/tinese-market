from django.db import models
from django.contrib.auth.models import User
from boutique.models import Product

class UserCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Panier de {self.user.username}"


class UserCartItem(models.Model):
    cart = models.ForeignKey(UserCart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"



