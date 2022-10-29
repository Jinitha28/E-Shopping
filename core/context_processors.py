from core.models import CartModel


def common_data(request):
    cart = None
    user = request.user
    if user.is_authenticated:
        cart = CartModel.get_cart(request)
    context = {
        "cart": cart,
    }

    return context
