from .cart import Cart
from .models import UserCart

def load_user_cart(request):
    if request.user.is_authenticated:
        try:
            user_cart = UserCart.objects.get(user=request.user)
            cart = Cart(request)
            cart.cart = {}

            for item in user_cart.items.all():
                cart.cart[str(item.product.id)] = {'qty': item.quantity}

            cart.save()
        except UserCart.DoesNotExist:
            pass
