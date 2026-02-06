from django.shortcuts import render
from boutique.models import Category, Product

def home(request):
    categories = Category.objects.all() if Category.objects.exists() else []
    products = Product.objects.all()[:8] if Product.objects.exists() else []

    return render(request, "home.html", {
        "categories": categories,
        "products": products,
    })


def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
