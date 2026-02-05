from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from boutique.models import Product
from cart.cart import Cart
from .models import Order, OrderItem, Payment
from .utils import send_order_confirmation
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_order(request):
    cart = Cart(request)

    if not cart.cart:
        return redirect('shop')

    order = Order.objects.create(
        user=request.user,
        total_price=cart.get_total_price()
    )

    send_order_confirmation(order)

    # 🔁 BOUCLE OBLIGATOIRE
    for product_id, item in cart.cart.items():
        product = Product.objects.get(id=product_id)

        # 🔴 Sécurité stock
        if product.stock < item['qty']:
            return redirect('cart_detail')

        OrderItem.objects.create(
            order=order,
            product=product,
            price=item['price'],
            quantity=item['qty']
        )

        # ✅ Décrément du stock
        product.stock -= item['qty']
        product.save()

    cart.clear()
    return redirect('order_summary', order_id=order.id)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'orders/order_detail.html', {
        'order': order
    })




@login_required
def payment_start(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # 🔒 Sécurité 1 : si la commande est déjà payée → bloquer
    if hasattr(order, 'payment') and order.payment.status == 'paid':
        return redirect('order_summary', order_id=order.id)

    # 🔒 Sécurité 2 : un seul paiement par commande
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.total_price,
            'status': 'pending',
            'method': 'stripe'
        }
    )

    return render(request, 'orders/payment_start.html', {
        'order': order,
        'payment': payment
    })


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/summary.html', {
        'order': order
    })



@login_required
def payment_choice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, 'orders/payment_choice.html', {
        'order': order
    })


@login_required
def payment_stripe(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # 🔒 Empêche double paiement
    if hasattr(order, 'payment') and order.payment.status == 'paid':
        return redirect('order_summary', order_id=order.id)

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount': order.total_price,
            'method': 'stripe',
            'status': 'pending'
        }
    )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': f'Commande #{order.id}',
                },
                'unit_amount': int(order.total_price * 100),
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

    return redirect(session.url)


    

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

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    payment = get_object_or_404(Payment, order=order)

    payment.status = 'paid'
    payment.save()

    return render(request, 'orders/payment_success.html', {
        'order': order
    })
