from django.urls import path, include
from core import views

app_name = "core"

urlpatterns = [

    #comman
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("feedback/create/", views.FeedbackCreateView.as_view(), name="feedback_create"),
    path("shop/", views.ShopView.as_view(), name="shop"),


    # User
    path("user/profile/create/", views.ProfileCreateView.as_view(), name="profile_create"),
    path("user/profile/<int:pk>/detail/", views.ProfileDetailView.as_view(), name="profile_detail"),
    path("user/profile/<int:pk>/update/", views.ProfileUpdateView.as_view(), name="profile_update"),
    path("user/profile/<int:pk>/address/create/", views.AddressCreateView.as_view(), name="address_create"),
    #path("user/address/create/", views.AddressCreateView.as_view(), name="address_create"),
    path("user/dashboard/", views.DashboardView.as_view(), name="dashboard"),


    #cart
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/product/<int:pk>/add/", views.AddToCartView.as_view(), name="cart_add"),
    path("cart/checkout/", views.CheckoutView.as_view(), name="checkout"),


    #product
    path("product/create/", views.ProductCreateView.as_view(), name="product_create"),
    path("product/list/", views.ProductListView.as_view(), name="product_list"),
    path("product/<int:pk>/detail/", views.ProductDetailView.as_view(), name="product_detail"),
    path("product/category", views.CategoryListView.as_view(), name="category_list"),
    path("product/category/<int:pk>/product/", views.ProductListByCategory.as_view(), name="product_by_category"),
    path("product/<int:pk>/review/", views.ProductReviewAddView.as_view(), name="add_product_review"),

    # Wishlist
    path("wishlist/", views.WishlistListView.as_view(), name="wishlist_list"),
    path("wishlist/create/", views.WishlistCreateView.as_view(), name="wishlist_create"),
    path("wishlist/<int:pk>/", views.WishlistDetailView.as_view(), name="wishlist_detail"),
    path("wishlist/add/product/<int:product_pk>/", views.AddToWishlist.as_view(), name="add_to_wishlist"),
    path("wishlist/remove/product/<int:product_pk>/", views.AddToWishlist.as_view(), name="remove_from_wishlist"),

    #registration
    path("user/signup/", views.RegistrationView.as_view(), name="signup"),
    path("user/login/", views.LoginView.as_view(), name="login"),
    path("user/logout/", views.LogoutView.as_view(), name="logout"),
    
    # Password Reset
    path("user/password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("user/password_reset/done/", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("user/reset/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("user/reset/done/", views.PasswordResetConfirmView.as_view(), name="password_reset_complete"),

    #order
    path("order/", views.OrderView.as_view(), name="order"),
    path("order/history/", views.OrderHistoryView.as_view(), name="order_history"),
    path("order/<str:pk>/", views.OrderDetailView.as_view(), name="order_detail"),

  # Payment
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path("paymentlist/", views.PaymentListView.as_view(), name="payment_list"),
    path("payment/response/", views.payment_handler, name="payment_handler"),


]
