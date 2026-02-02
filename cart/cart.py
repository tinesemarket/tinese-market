class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, qty=1):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'qty': 0,
                'price': float(product.price),
                'name': product.name,
                'image': product.image.url if product.image else ''
            }

        self.cart[product_id]['qty'] += qty
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def decrease(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['qty'] -= 1
            if self.cart[product_id]['qty'] <= 0:
                del self.cart[product_id]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def total_quantity(self):
        return sum(item['qty'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            item['price'] * item['qty']
            for item in self.cart.values()
        )
