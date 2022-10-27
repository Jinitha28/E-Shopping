from core.models import Cart


def common_data(request):
    cart = None
    user = request.user
    if user.is_authenticated:
        cart = Cart.get_cart(request)
    context = {
        "cart": cart,
    }

    return context
