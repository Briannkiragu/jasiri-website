from dataclasses import dataclass
from decimal import Decimal

from .models import Product


MAX_QUANTITY = 99


@dataclass(frozen=True)
class CartItem:
    product: Product
    quantity: int

    @property
    def subtotal(self) -> Decimal:
        return self.product.price * self.quantity


def get_cart_items(session) -> list[CartItem]:
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        return []

    product_ids = []
    quantities = {}
    for product_id, quantity in cart.items():
        if (
            str(product_id).isdigit()
            and isinstance(quantity, int)
            and not isinstance(quantity, bool)
            and 1 <= quantity <= MAX_QUANTITY
        ):
            normalized_id = str(int(product_id))
            product_ids.append(int(normalized_id))
            quantities[normalized_id] = quantity

    products = Product.objects.filter(is_active=True, pk__in=product_ids)
    return [
        CartItem(product=product, quantity=quantities[str(product.pk)])
        for product in products
    ]
