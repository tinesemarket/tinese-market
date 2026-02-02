from django.shortcuts import render, redirect, get_object_or_404
from boutique.models import Product
from .cart import Cart


def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        return redirect('shop')  # sécurité backend

    cart.add(product)
    return redirect('cart_detail')



def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def decrease_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.decrease(product)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {
        'cart': cart.cart,
        'total_price': cart.get_total_price()
    })


