from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop, name='shop'),
    path('<slug:category_slug>/', views.shop_by_category, name='shop_by_category'),
]

