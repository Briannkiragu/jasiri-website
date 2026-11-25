def cart_count(request):
    cart = request.session.get("cart", {})
    cart_updated = request.session.pop("cart_updated", False)
    if not isinstance(cart, dict):
        return {"cart_count": 0, "cart_updated": cart_updated}

    count = 0
    for quantity in cart.values():
        if (
            isinstance(quantity, int)
            and not isinstance(quantity, bool)
            and 1 <= quantity <= 99
        ):
            count += quantity
    return {"cart_count": count, "cart_updated": cart_updated}
