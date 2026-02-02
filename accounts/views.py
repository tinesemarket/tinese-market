from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from boutique.models import Product
from cart.models import UserCart, UserCartItem
from cart.cart import Cart
from cart.utils import load_user_cart
from django.contrib.auth.decorators import login_required
from orders.models import Order


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Charger le panier utilisateur en session
            load_user_cart(request)

            # Sauvegarder le panier session en base
            session_cart = Cart(request)
            user_cart, created = UserCart.objects.get_or_create(user=user)

            for product_id, item in session_cart.cart.items():
                product = Product.objects.get(id=product_id)
                cart_item, created = UserCartItem.objects.get_or_create(
                    cart=user_cart,
                    product=product
                )
                cart_item.quantity += item['qty']
                cart_item.save()

            request.session['cart'] = {}
            return redirect('shop')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('shop')


def register_view(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('login')

    return render(request, 'accounts/register.html', {
        'form': form
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {
        'orders': orders
    })