from django.urls import include, re_path, path
from django.contrib.auth import views as auth_views
from . import views
# app_name = 'shop'
urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"^product/(?P<product_id>[0-9]+)$", views.view_product_detail, name="view_product_detail"),
    re_path(r"^add-product/(?P<product_id>[0-9]+)$", views.add_product_to_cart, name="add_product_to_cart"),
    re_path(r"^cart$", views.show_cart, name="show_cart"),
    path("cart/<int:product_id>/<str:action>", views.change_product_quantity, name='change_product_quantity'),
    re_path(r"^cart-remove/(?P<product_id>[0-9]+)$", views.remove_product_in_cart, name="remove_product_in_cart"),
    re_path(r"^confirm$", views.confirm_checkout, name="confirm_checkout"),
    re_path(r"^checkout$", views.checkout, name="checkout"),
    # re_path(r"^cart/(?P<product_id>[0-9]+)/(?P<action>[in|de]crease)$", views.change_product_quantity, name='change_product_quantity'),

    re_path(r"^register$", views.register_user, name="register"),
    re_path(r"^login$", views.login_user, name="login"),
    re_path(r"^logout$", auth_views.LogoutView.as_view(next_page='/'), name="logout"),
]