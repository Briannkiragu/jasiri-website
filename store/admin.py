from django.contrib import admin

from .models import NewsletterSubscriber, Payment, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "is_active")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")
    search_fields = ("email",)
    ordering = ("-created_at",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "paypal_order_id",
        "status",
        "amount",
        "currency",
        "user",
        "created_at",
    )
    list_filter = ("status", "currency")
    search_fields = ("paypal_order_id", "paypal_capture_id", "user__email")
    readonly_fields = (
        "paypal_order_id",
        "paypal_capture_id",
        "amount",
        "currency",
        "cart_snapshot",
        "created_at",
        "updated_at",
    )
