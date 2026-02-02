from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation(order):
    subject = f"Confirmation de commande #{order.id}"
    message = f"""
Bonjour {order.user.username},

Merci pour votre commande sur Tinese Market 🛍

🧾 Commande : #{order.id}
💰 Total : {order.total_price} FCFA

Nous vous contacterons pour la livraison.

— Tinese Market
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=True,
    )
