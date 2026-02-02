from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('pay/<int:order_id>/', views.payment_start, name='payment_start'),
    path('summary/<int:order_id>/', views.order_summary, name='order_summary'),
    path('pay/<int:order_id>/', views.payment_choice, name='payment_choice'),
    path('pay/stripe/<int:order_id>/', views.payment_stripe, name='payment_stripe'),
    path('pay/mobile/<int:order_id>/', views.mobile_payment, name='mobile_payment'),
]


