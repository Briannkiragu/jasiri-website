from decimal import Decimal
import json
import logging
import smtplib
import urllib.error
import urllib.parse
import urllib.request

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.db import transaction
from django.db.models import Case, IntegerField, When
from django.conf import settings
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import MAX_QUANTITY, get_cart_items
from .emails import send_templated_email
from .forms import NewsletterSignupForm, RegistrationForm
from .models import NewsletterSubscriber, Payment, Product

logger = logging.getLogger(__name__)


def home(request):
    featured_slugs = [
        "statement-graphic-tee",
        "limited-graphic-tee",
        "classic-tee",
        "essential-graphic-tee",
    ]
    products = Product.objects.filter(is_active=True, slug__in=featured_slugs).order_by(
        Case(
            *[When(slug=slug, then=position) for position, slug in enumerate(featured_slugs)],
            output_field=IntegerField(),
        )
    )
    return render(request, "store/home.html", {"products": products})


def shop_landing(request):
    return render(request, "store/shop.html")


def about(request):
    return render(request, "store/about.html")


def support(request):
    return render(request, "store/support.html")


def blog(request):
    return render(request, "store/blog.html")


def blog_gallery(request, gallery):
    galleries = {
        "first": ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"],
        "second": ["7.jpg", "8.jpg", "10.jpg", "11.jpg", "12.jpg", "13.jpg", "14.jpg"],
    }
    images = galleries.get(gallery)
    if images is None:
        return render(request, "store/not_found.html", status=404)
    return render(
        request,
        "store/blog_gallery.html",
        {"images": images, "gallery": gallery},
    )


def product_list(request, category=None):
    products = Product.objects.filter(is_active=True)
    title = "Shop the collection"
    if category:
        category_values = {
            "tees": (Product.Category.TEE, "Tees"),
            "jackets": (Product.Category.JACKET, "Jackets"),
        }
        selected_category = category_values.get(category)
        if selected_category is None:
            return render(request, "store/not_found.html", status=404)
        products = products.filter(category=selected_category[0])
        title = selected_category[1]

    return render(
        request,
        "store/product_list.html",
        {"products": products, "title": title},
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    recommendations = Product.objects.filter(
        is_active=True,
        category=product.category,
    ).exclude(pk=product.pk)[:4]
    return render(
        request,
        "store/product_detail.html",
        {"product": product, "recommendations": recommendations},
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("store:account")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            context = {
                "user": user,
                "domain": request.get_host(),
                "protocol": "https" if request.is_secure() else "http",
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            }
            send_templated_email(
                "Verify your Jasiri account",
                "account_verification",
                context,
                user.email,
            )
        messages.success(
            request,
            "Check your email to verify your account before signing in.",
        )
        return redirect("login")
    return render(request, "store/register.html", {"form": form})


def activate_account(request, uidb64, token):
    user_model = get_user_model()
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = user_model.objects.get(pk=user_id, is_active=False)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        messages.success(request, "Your email is verified. You can now sign in.")
        return redirect("login")
    return render(request, "store/activation_invalid.html", status=400)


@login_required
def account(request):
    return render(request, "store/account.html")


def cart_detail(request):
    items = get_cart_items(request.session)
    total = sum((item.subtotal for item in items), Decimal("0.00"))
    return render(request, "store/cart.html", {"items": items, "total": total})


def _cart_redirect(request, fallback):
    referrer = request.META.get("HTTP_REFERER", "")
    if url_has_allowed_host_and_scheme(
        referrer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(referrer)
    return redirect(fallback)


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        messages.error(request, "Enter a valid quantity.")
        return _cart_redirect(request, "store:cart_detail")

    if not 1 <= quantity <= MAX_QUANTITY:
        messages.error(request, f"Quantity must be between 1 and {MAX_QUANTITY}.")
        return _cart_redirect(request, "store:cart_detail")

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    product_key = str(product.pk)
    current_quantity = cart.get(product_key, 0)
    if (
        not isinstance(current_quantity, int)
        or isinstance(current_quantity, bool)
        or not 1 <= current_quantity <= MAX_QUANTITY
    ):
        current_quantity = 0
    updated_quantity = current_quantity + quantity
    if updated_quantity > MAX_QUANTITY:
        messages.error(request, f"You can add up to {MAX_QUANTITY} of one item.")
        return _cart_redirect(request, "store:cart_detail")

    cart[product_key] = updated_quantity
    request.session["cart"] = cart
    request.session["cart_updated"] = True
    messages.success(request, f"{product.name} added to your cart.")
    return _cart_redirect(request, "store:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", ""))
    except (TypeError, ValueError):
        messages.error(request, "Enter a valid quantity.")
        return redirect("store:cart_detail")

    if not 1 <= quantity <= MAX_QUANTITY:
        messages.error(request, f"Quantity must be between 1 and {MAX_QUANTITY}.")
        return redirect("store:cart_detail")

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict) or str(product.pk) not in cart:
        messages.error(request, "That product is no longer in your cart.")
        return redirect("store:cart_detail")
    cart[str(product.pk)] = quantity
    request.session["cart"] = cart
    request.session["cart_updated"] = True
    messages.success(request, "Cart updated.")
    return redirect("store:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = request.session.get("cart", {})
    if isinstance(cart, dict):
        cart.pop(str(product_id), None)
        request.session["cart"] = cart
        request.session["cart_updated"] = True
    messages.success(request, "Item removed from your cart.")
    return redirect("store:cart_detail")


@require_POST
def newsletter_signup(request):
    form = NewsletterSignupForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"]
        _, created = NewsletterSubscriber.objects.get_or_create(
            email=email
        )
        email_sent = True
        if created:
            try:
                email_sent = send_templated_email(
                    "Welcome to Jasiri",
                    "newsletter_welcome",
                    {},
                    email,
                )
            except (OSError, smtplib.SMTPException):
                email_sent = False
                logger.exception("Could not send newsletter welcome email")
        if email_sent:
            messages.success(
                request,
                "Welcome to the rebellion!",
                extra_tags="newsletter",
            )
        else:
            messages.warning(
                request,
                "You are subscribed, but we could not send the welcome email.",
                extra_tags="newsletter",
            )
    else:
        messages.error(request, "Please enter a valid email address.")

    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("store:home")


def checkout(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    items = get_cart_items(request.session)
    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect("store:cart_detail")
    total = sum((item.subtotal for item in items), Decimal("0.00"))
    return render(
        request,
        "store/checkout.html",
        {
            "items": items,
            "total": total,
            "paypal_client_id": settings.PAYPAL_CLIENT_ID,
            "paypal_currency": settings.PAYPAL_CURRENCY,
            "paypal_is_configured": bool(
                settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET
            ),
        },
    )


def _paypal_api_base():
    if settings.PAYPAL_MODE == "live":
        return "https://api-m.paypal.com"
    return "https://api-m.sandbox.paypal.com"


def _paypal_request(path, method="POST", data=None):
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        raise RuntimeError("PayPal credentials are not configured.")

    token_request = urllib.request.Request(
        f"{_paypal_api_base()}/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    credentials = f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}"
    import base64

    token_request.add_header(
        "Authorization",
        f"Basic {base64.b64encode(credentials.encode('ascii')).decode('ascii')}",
    )
    try:
        with urllib.request.urlopen(token_request, timeout=15) as response:
            token_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise _paypal_http_error(exc) from exc
    access_token = token_payload.get("access_token")
    if not access_token:
        raise RuntimeError("PayPal did not issue an access token.")

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    request = urllib.request.Request(
        f"{_paypal_api_base()}{path}",
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise _paypal_http_error(exc) from exc


def _paypal_http_error(error):
    try:
        payload = json.loads(error.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return RuntimeError(f"PayPal returned HTTP {error.code}.")

    details = [
        detail.get("description")
        for detail in payload.get("details", [])
        if detail.get("description")
    ]
    message = payload.get("message") or payload.get("name") or "request rejected"
    if details:
        message = f"{message}: {'; '.join(details)}"
    return RuntimeError(f"PayPal returned HTTP {error.code}: {message}")


@require_POST
def paypal_create_order(request):
    items = get_cart_items(request.session)
    if not items:
        return JsonResponse({"error": "Your cart is empty."}, status=400)

    total = sum((item.subtotal for item in items), Decimal("0.00")).quantize(
        Decimal("0.01")
    )
    currency = settings.PAYPAL_CURRENCY
    snapshot = [
        {
            "product_id": item.product.pk,
            "name": item.product.name,
            "price": str(item.product.price),
            "quantity": item.quantity,
        }
        for item in items
    ]

    try:
        payload = _paypal_request(
            "/v2/checkout/orders",
            data={
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": currency,
                            "value": format(total, ".2f"),
                        },
                    }
                ],
            },
        )
    except (RuntimeError, urllib.error.URLError, TimeoutError) as exc:
        logger.exception("Unable to create PayPal order")
        return JsonResponse({"error": str(exc)}, status=503)

    order_id = payload.get("id")
    if not order_id:
        return JsonResponse({"error": "PayPal did not return an order ID."}, status=502)

    Payment.objects.create(
        user=request.user if request.user.is_authenticated else None,
        paypal_order_id=order_id,
        amount=total,
        currency=currency,
        status=Payment.Status.CREATED,
        cart_snapshot={"items": snapshot},
    )
    request.session["paypal_checkout_order_id"] = order_id
    return JsonResponse({"id": order_id})


@require_POST
def paypal_capture_order(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request."}, status=400)

    order_id = body.get("orderID")
    if not order_id:
        return JsonResponse({"error": "Missing PayPal order ID."}, status=400)
    if request.session.get("paypal_checkout_order_id") != order_id:
        return JsonResponse({"error": "This PayPal order is not for this checkout."}, status=400)

    payment = get_object_or_404(Payment, paypal_order_id=order_id)
    if payment.status == Payment.Status.COMPLETED:
        return JsonResponse({"status": "COMPLETED"})

    try:
        payload = _paypal_request(
            f"/v2/checkout/orders/{urllib.parse.quote(order_id, safe='')}/capture"
        )
    except (RuntimeError, urllib.error.URLError, TimeoutError) as exc:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status", "updated_at"])
        logger.exception("Unable to capture PayPal order %s", order_id)
        return JsonResponse({"error": str(exc)}, status=503)

    capture = None
    for unit in payload.get("purchase_units", []):
        for captured in unit.get("payments", {}).get("captures", []):
            if captured.get("status") == "COMPLETED":
                capture = captured
                break
        if capture:
            break

    if payload.get("status") != "COMPLETED" or not capture:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status", "updated_at"])
        return JsonResponse({"error": "PayPal did not complete the capture."}, status=502)

    capture_amount = Decimal(capture["amount"]["value"])
    capture_currency = capture["amount"]["currency_code"]
    if capture_amount != payment.amount or capture_currency != payment.currency:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status", "updated_at"])
        logger.error("PayPal capture mismatch for order %s", order_id)
        return JsonResponse({"error": "The captured amount does not match the order."}, status=400)

    payment.paypal_capture_id = capture["id"]
    payment.status = Payment.Status.COMPLETED
    payment.save(
        update_fields=[
            "paypal_capture_id",
            "status",
            "updated_at",
        ]
    )
    request.session.pop("cart", None)
    request.session.pop("paypal_checkout_order_id", None)
    return JsonResponse({"status": "COMPLETED"})
