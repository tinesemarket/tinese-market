from .cart import Cart

def cart_info(request):
    cart = Cart(request)
    return {
        'cart_count': cart.total_quantity()
    }
