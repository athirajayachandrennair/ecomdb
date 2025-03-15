from django.urls import path
from .import views
from .views import download_invoice

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
      path('logout/', views.logout_user, name='logout'),

    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
   
    path('order/place/', views.place_order, name='place_order'),
    path('order/success/', views.order_success, name='order_success'),

     path('orders/history/', views.purchase_history, name='purchase_history'),

      path('order/invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

    
   

    
]