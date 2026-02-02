from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "boutique/shop.html", {
        "products": products,
        "categories": categories
    })

def shop_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()

    return render(request, "boutique/shop.html", {
        "products": products,
        "categories": categories,
        "active_category": category
    })
