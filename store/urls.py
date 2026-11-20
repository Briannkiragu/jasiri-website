from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("accounts/register/", views.register, name="register"),
    path(
        "accounts/activate/<uidb64>/<token>/",
        views.activate_account,
        name="activate_account",
    ),
    path("accounts/me/", views.account, name="account"),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("support/", views.support, name="support"),
    path("blog/", views.blog, name="blog"),
    path("blog/gallery/<slug:gallery>/", views.blog_gallery, name="blog_gallery"),
    path("shop/", views.shop_landing, name="shop_landing"),
    path("products/", views.product_list, name="product_list"),
    path("shop/tees/", views.product_list, {"category": "tees"}, name="tee_list"),
    path(
        "shop/jackets/",
        views.product_list,
        {"category": "jackets"},
        name="jacket_list",
    ),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("newsletter/subscribe/", views.newsletter_signup, name="newsletter_signup"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "checkout/paypal/create/",
        views.paypal_create_order,
        name="paypal_create_order",
    ),
    path(
        "checkout/paypal/capture/",
        views.paypal_capture_order,
        name="paypal_capture_order",
    ),
]
