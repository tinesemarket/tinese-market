from django.shortcuts import render
from boutique.models import Category, Product

def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(stock__gt=0)[:8]

    return render(request, "home.html", {
        "categories": categories,
        "products": products,
    })



def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
