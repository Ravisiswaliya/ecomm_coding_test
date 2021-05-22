from django.urls import path, re_path, include
from uauth import views

urlpatterns = [
    path("login-view", views.LoginViewView.as_view(), name='login-view'),
    path("seller-view", views.SellerView.as_view(), name='seller-view'),
    path("product-view", views.ProductList.as_view(), name='product-view'),
    path("product/<int:pk>", views.SellProduct.as_view(), name='product-view'),
]