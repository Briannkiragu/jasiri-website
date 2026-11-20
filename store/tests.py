import io
import re
import urllib.error

from django.core import mail
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .cart import MAX_QUANTITY
from .models import NewsletterSubscriber, Product
from .views import _paypal_http_error


class StoreViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            name="Test Tee",
            slug="test-tee",
            category=Product.Category.TEE,
            price="1200.00",
            image="Mwanzocollection/tees/9.jpg",
        )

    def test_seeded_catalog_is_available(self):
        self.assertEqual(Product.objects.exclude(slug="test-tee").count(), 16)
        response = self.client.get(reverse("store:product_list"))
        self.assertContains(response, "Essential Graphic Tee")

    def test_home_and_product_detail_render(self):
        home_response = self.client.get(reverse("store:home"))
        detail_response = self.client.get(self.product.get_absolute_url())
        self.assertContains(home_response, "Wear your own")
        self.assertContains(home_response, "site-footer")
        self.assertContains(detail_response, "Test Tee")

    def test_footer_links_are_shared_and_working_on_main_pages(self):
        routes = (
            "store:home",
            "store:shop_landing",
            "store:about",
            "store:blog",
        )
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                content = response.content.decode()
                footer = re.search(r"<footer\b.*?</footer>", content, re.DOTALL)
                self.assertIsNotNone(footer)
                footer_html = footer.group(0)

                for heading in ("Contact", "About", "My account", "Follow us"):
                    self.assertIn(f"<h4>{heading}</h4>", footer_html)

                for destination in (
                    reverse("store:about"),
                    reverse("store:support"),
                    reverse("store:cart_detail"),
                ):
                    self.assertIn(f'href="{destination}"', footer_html)
                self.assertNotIn('href="#"', footer_html)
                self.assertIn("https://www.instagram.com/jas1ri/", footer_html)
                self.assertIn("https://wa.me/254705061968", footer_html)
                self.assertNotIn("pinterest", footer_html.lower())

    def test_support_page_is_available(self):
        response = self.client.get(reverse("store:support"))
        self.assertContains(response, "Contact &amp; Support")
        self.assertContains(response, "current delivery information")
        self.assertContains(response, "wa.me/254705061968")

    def test_shop_landing_preserves_category_cards(self):
        response = self.client.get(reverse("store:shop_landing"))
        self.assertContains(response, "Find your next favourite")
        self.assertContains(response, reverse("store:tee_list"))
        self.assertContains(response, reverse("store:jacket_list"))
        header = self._header_navigation(response)
        self.assertNotIn(">Tees</a>", header)
        self.assertNotIn(">Jackets</a>", header)

    def test_newsletter_section_is_before_footer_on_selected_pages_only(self):
        selected_routes = (
            "store:shop_landing",
            "store:about",
            "store:blog",
        )
        for route in selected_routes:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertContains(response, 'class="newsletter-signup"')
                content = response.content.decode()
                self.assertLess(
                    content.index('class="newsletter-signup"'),
                    content.index("<footer"),
                )

        excluded_routes = (
            "store:home",
            "store:product_list",
        )
        for route in excluded_routes:
            with self.subTest(route=route):
                self.assertNotContains(
                    self.client.get(reverse(route)),
                    'class="newsletter-signup"',
                )

        gallery = self.client.get(reverse("store:blog_gallery", args=["first"]))
        self.assertNotContains(gallery, 'class="newsletter-signup"')

    def test_about_and_blog_pages_are_available(self):
        about_response = self.client.get(reverse("store:about"))
        blog_response = self.client.get(reverse("store:blog"))
        self.assertContains(about_response, "FREEDOM ARC")
        self.assertContains(blog_response, "Waasi Studio")
        self.assertContains(blog_response, reverse("store:blog_gallery", args=["first"]))
        for response in (about_response, blog_response):
            header = self._header_navigation(response)
            self.assertNotIn(">Tees</a>", header)
            self.assertNotIn(">Jackets</a>", header)

    def test_category_links_are_not_in_catalog_header(self):
        response = self.client.get(reverse("store:tee_list"))
        header = self._header_navigation(response)
        self.assertNotIn(">Tees</a>", header)
        self.assertNotIn(">Jackets</a>", header)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_newsletter_signup_normalizes_and_deduplicates_emails(self):
        signup_url = reverse("store:newsletter_signup")
        return_url = reverse("store:shop_landing")
        response = self.client.post(
            signup_url,
            {"email": "NEWSLETTER@EXAMPLE.COM", "next": return_url},
        )
        self.assertRedirects(response, return_url, fetch_redirect_response=False)
        signup_landing = self.client.get(return_url)
        self.assertContains(signup_landing, "Welcome to the rebellion!")
        self.assertContains(signup_landing, "store/newsletter-alert.js")
        self.assertTrue(
            NewsletterSubscriber.objects.filter(email="newsletter@example.com").exists()
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["newsletter@example.com"])
        self.assertIn("Welcome to the rebellion!", mail.outbox[0].body)

        self.client.post(
            signup_url,
            {"email": "newsletter@example.com", "next": return_url},
        )
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_newsletter_signup_rejects_invalid_email(self):
        response = self.client.post(
            reverse("store:newsletter_signup"),
            {"email": "not-an-email"},
        )
        self.assertRedirects(response, reverse("store:home"))
        self.assertEqual(NewsletterSubscriber.objects.count(), 0)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_registration_requires_email_verification_before_login(self):
        response = self.client.post(
            reverse("store:register"),
            {
                "username": "new-customer",
                "email": "CUSTOMER@example.com",
                "password1": "S0mething-Very-Long!42",
                "password2": "S0mething-Very-Long!42",
            },
        )
        self.assertRedirects(
            response,
            reverse("login"),
            fetch_redirect_response=False,
        )
        user = get_user_model().objects.get(username="new-customer")
        self.assertFalse(user.is_active)
        self.assertEqual(user.email, "customer@example.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/activate/", mail.outbox[0].body)
        self.assertEqual(len(mail.outbox[0].alternatives), 1)

        match = re.search(
            r"http://testserver(/accounts/activate/[\w-]+/[\w-]+/)",
            mail.outbox[0].body,
        )
        self.assertIsNotNone(match)
        activation_response = self.client.get(match.group(1))
        self.assertEqual(activation_response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(
            self.client.login(
                username="new-customer",
                password="S0mething-Very-Long!42",
            )
        )

    def test_account_requires_login_and_logout_clears_session(self):
        account_url = reverse("store:account")
        response = self.client.get(account_url)
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={account_url}",
            fetch_redirect_response=False,
        )

        user = get_user_model().objects.create_user(
            username="customer",
            email="customer@example.com",
            password="S0mething-Very-Long!42",
        )
        self.assertTrue(
            self.client.login(
                username=user.username,
                password="S0mething-Very-Long!42",
            )
        )
        self.assertContains(self.client.get(account_url), "customer@example.com")

        logout_response = self.client.post(reverse("logout"))
        self.assertRedirects(
            logout_response,
            reverse("store:home"),
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            self.client.get(account_url),
            f"{reverse('login')}?next={account_url}",
            fetch_redirect_response=False,
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_uses_email_template(self):
        get_user_model().objects.create_user(
            username="reset-customer",
            email="reset@example.com",
            password="S0mething-Very-Long!42",
        )
        response = self.client.post(
            reverse("password_reset"),
            {"email": "reset@example.com"},
        )
        self.assertRedirects(
            response,
            reverse("password_reset_done"),
            fetch_redirect_response=False,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Reset your Jasiri password")
        self.assertIn("/accounts/reset/", mail.outbox[0].body)
        self.assertEqual(len(mail.outbox[0].alternatives), 1)

    def _header_navigation(self, response):
        content = response.content.decode()
        match = re.search(r'<ul id="navbar">(.*?)</ul>', content, re.DOTALL)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_blog_photo_stories_are_available(self):
        first_story = self.client.get(
            reverse("store:blog_gallery", args=["first"])
        )
        second_story = self.client.get(
            reverse("store:blog_gallery", args=["second"])
        )
        self.assertContains(first_story, "AdobeLightroom/1.jpg")
        self.assertContains(second_story, "AdobeLightroom/14.jpg")

    def test_category_filters_products(self):
        response = self.client.get(reverse("store:jacket_list"))
        self.assertContains(response, "Essential Utility Jacket")
        self.assertNotContains(response, "Test Tee")

    def test_add_update_and_remove_cart_items(self):
        add_url = reverse("store:cart_add", args=[self.product.pk])
        response = self.client.post(add_url, {"quantity": "2"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 2)

        cart_response = self.client.get(reverse("store:cart_detail"))
        self.assertContains(cart_response, 'class="cart-count-indicator is-updated"', count=2)
        self.assertContains(cart_response, ">2<", count=2)

        update_url = reverse("store:cart_update", args=[self.product.pk])
        self.client.post(update_url, {"quantity": "3"})
        cart_response = self.client.get(reverse("store:cart_detail"))
        self.assertContains(cart_response, "KSh 3600")

        remove_url = reverse("store:cart_remove", args=[self.product.pk])
        self.client.post(remove_url)
        self.assertNotIn(str(self.product.pk), self.client.session["cart"])

    def test_cart_rejects_invalid_quantities(self):
        add_url = reverse("store:cart_add", args=[self.product.pk])
        for quantity in ("0", str(MAX_QUANTITY + 1), "invalid"):
            with self.subTest(quantity=quantity):
                self.client.post(add_url, {"quantity": quantity})
                self.assertNotIn(str(self.product.pk), self.client.session.get("cart", {}))

    def test_inactive_product_cannot_be_added_to_cart(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.post(
            reverse("store:cart_add", args=[self.product.pk]),
            {"quantity": "1"},
        )
        self.assertEqual(response.status_code, 404)

    def test_checkout_requires_items_and_can_render_without_paypal_credentials(self):
        empty_response = self.client.post(reverse("store:checkout"))
        self.assertRedirects(
            empty_response,
            reverse("store:cart_detail"),
            fetch_redirect_response=False,
        )

        self.client.post(
            reverse("store:cart_add", args=[self.product.pk]),
            {"quantity": "2"},
        )
        with override_settings(PAYPAL_CLIENT_ID="", PAYPAL_CLIENT_SECRET=""):
            response = self.client.post(reverse("store:checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PayPal sandbox credentials are not configured")
        self.assertContains(response, "KSh 2400")

    def test_paypal_create_order_requires_items(self):
        response = self.client.post(reverse("store:paypal_create_order"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["error"].lower())

    def test_paypal_api_errors_include_provider_reason(self):
        error = urllib.error.HTTPError(
            "https://api-m.sandbox.paypal.com/v2/checkout/orders",
            422,
            "Unprocessable Entity",
            {},
            io.BytesIO(
                b'{"name":"UNPROCESSABLE_ENTITY","message":"Invalid request",'
                b'"details":[{"description":"Currency is not supported"}]}'
            ),
        )

        message = str(_paypal_http_error(error))
        self.assertIn("HTTP 422", message)
        self.assertIn("Currency is not supported", message)
