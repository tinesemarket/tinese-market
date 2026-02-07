from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db import transaction

from boutique.models import Product
from cart.cart import Cart
from .models import Order, OrderItem, Payment
from .utils import send_order_confirmation


# =========================
# 🔐 STRIPE SAFE LOADER
# =========================
def get_stripe_key():
    """
    Retourne la clé Stripe si elle existe.
    Ne fait JAMAIS planter Django.
    """
    key = getattr(settings, "STRIPE_SECRET_KEY", None)
    if not key or not isinstance(key, str) or key.strip() == "":
        return None
    return key


# =========================
# 🛒 CRÉATION COMMANDE
# =========================
@login_required
@transaction.atomic
def create_order(request):
    cart = Cart(request)

    if not cart.cart:
        return redirect('shop')

    order = Order.objects.create(
        user=request.user,
        total_price=cart.get_total_price()
    )

    send_order_confirmation(order)

    for product_id, item in cart.cart.items():
        product = get_object_or_404(
            Product.objects.select_for_update(),
            id=product_id
        )

        if product.stock < item['qty']:
            return redirect('cart_detail')

        OrderItem.objects.create(
            order=order,
            product=product,
            price=item['price'],
            quantity=item['qty']
        )

        product.stock -= item['qty']
        product.save()

    cart.clear()
    return redirect('order_summary', order_id=order.id)


# =========================
# 📄 DÉTAIL COMMANDE
# =========================
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


# =========================
# 💳 CHOIX PAIEMENT
# =========================
@login_required
def payment_choice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/payment_choice.html', {'order': order})


# =========================
# 💳 DÉMARRAGE PAIEMENT
# =========================
@login_required
def payment_start(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if hasattr(order, 'payment') and order.payment.status == 'paid':
        return redirect('order_summary', order_id=order.id)

    Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.total_price,
            'status': 'pending',
            'method': 'stripe'
        }
    )

    return render(request, 'orders/payment_start.html', {'order': order})


# =========================
# 💳 STRIPE CHECKOUT
# =========================
@login_required
def payment_stripe(request, order_id):
    stripe_key = get_stripe_key()

    if stripe_key is None:
        return render(request, 'orders/payment_unavailable.html')

    import stripe
    stripe.api_key = stripe_key

    order = get_object_or_404(Order, id=order_id, user=request.user)

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.total_price,
            'method': 'stripe',
            'status': 'pending'
        }
    )

    if payment.status == 'paid':
        return redirect('order_summary', order_id=order.id)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Commande #{order.id}',
                    },
                    'unit_amount': int(float(order.total_price) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                f'/orders/success/{order.id}/'
            ),
            cancel_url=request.build_absolute_uri(
                f'/orders/summary/{order.id}/'
            ),
        )
    except stripe.error.StripeError:
        return render(request, 'orders/payment_error.html', {'order': order})

    return redirect(session.url)


# =========================
# 📱 MOBILE MONEY
# =========================
@login_required
def mobile_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.total_price,
            'method': 'mobile',
            'status': 'pending'
        }
    )

    return render(request, 'orders/mobile_instructions.html', {'order': order})


# =========================
# ✅ SUCCÈS PAIEMENT
# =========================
@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = get_object_or_404(Payment, order=order)

    payment.status = 'paid'
    payment.save()

    return render(request, 'orders/payment_success.html', {'order': order})


# =========================
# 📄 RÉCAP
# =========================
@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/summary.html', {'order': order})
