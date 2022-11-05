import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import mixins as auth_mixins
from django.contrib.auth import views as auth_views
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic as views

from core import forms as core_forms
from core import models as core_models
from core import payment

USER = get_user_model()
RAZORPAY_CLIENT = payment.get_client()


# Home View
class HomeView(views.TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = core_models.ProductModel.objects.filter(status=True).order_by(
            "reviewmodel__rating"
        )[:10]
        context["products"] = products
        return context


# About View
class AboutView(views.TemplateView):
    template_name = "core/about.html"


# Contact view
class FeedbackCreateView(SuccessMessageMixin, views.CreateView):
    template_name = "core/feedback/create.html"
    form_class = core_forms.FeedbackForm
    success_url = reverse_lazy("core:home")
    success_message = "Mail sent successfully!"

    def form_valid(self, form):
        data = form.cleaned_data
        name = data.get("name")
        subject = "Thanks for your valuable feedback"
        to_email = data.get("email")
        message = f"""
        Hi {name},
        
        Thank you for your valuable feedback. We will reach you very soon.
        (This is a auto generated mail.)
        
        Thank you,
        E-shopping Team
        """
        from_email = settings.EMAIL_HOST_USER
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[
                    to_email,
                ],
            )
        except:
            return super().form_invalid(form)
        return super().form_valid(form)


# Shop view
class ShopView(views.ListView):
    template_name = "shop/shop.html"
    model = core_models.ProductModel
    paginate_by = 10
    context_object_name = "products"


# Profile Create View
class ProfileCreateView(
    auth_mixins.LoginRequiredMixin, SuccessMessageMixin, views.CreateView
):
    template_name = "user/profile/create.html"
    form_class = core_forms.ProfileForm
    success_message = "Profile created successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ProfileDetailView(auth_mixins.LoginRequiredMixin, views.DetailView):
    template_name = "user/profile/detail.html"
    model = core_models.ProfileModel


class ProfileUpdateView(
    auth_mixins.LoginRequiredMixin, SuccessMessageMixin, views.UpdateView
):
    template_name = "user/profile/update.html"
    model = core_models.ProfileModel
    form_class = core_forms.ProfileForm
    success_message = "Profile updated successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# Address create view
class AddressCreateView(
    auth_mixins.LoginRequiredMixin, SuccessMessageMixin, views.CreateView
):
    template_name = "user/address/create.html"
    model = core_models.AddressModel
    form_class = core_forms.AddressForm
    success_message = "Address created successfully!"

    def form_valid(self, form):
        user = self.request.user

        if user.has_profile():
            address = form.save()
            user.profile.address.add(address)
            user.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        pk = self.kwargs.get("pk", None)
        if pk:
            url = reverse_lazy(
                "core:profile_detail", kwargs={"pk": self.kwargs.get("pk")}
            )
        else:
            url = self.request.META.get("HTTP_REFERER")
        return url


# Dashboard view
class DashboardView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "user/dashboard.html"

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        user = self.request.user
        cart = core_models.CartModel.get_cart(self.request)
        orders = core_models.OrderModel.objects.filter(cart__user=user)
        payments = core_models.PaymentModel.objects.filter(order__cart__user=user)

        context = {
            "cart": cart,
            "orders": orders,
            "payments": payments,
        }
        context.update(kwargs)
        return context


# registration view
class RegistrationView(views.CreateView):
    template_name = "registration/signup.html"
    model = USER
    form_class = core_forms.UserRegistrationForm
    success_url = reverse_lazy("core:login")


# login view
class LoginView(auth_views.LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    enable_recaptcha = True
    extra_context = {
        "reCAPTCHA_site_key" : settings.GOOGLE_RECAPTCHA_SITE_KEY
    }

    def form_valid(self, form):
        print("GOOGLE_RECAPTCHA_:=========", settings.GOOGLE_RECAPTCHA_SITE_KEY)
        verified = True
        if self.enable_recaptcha:
            g_recaptcha_response = self.request.POST.get("g-recaptcha-response")
            url = settings.GOOGLE_RECAPTCHA_VERIFICATION_URL
            data = {
                "secret": settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                "response": g_recaptcha_response,
            }
            # Getting response from recaptcha server
            response = requests.post(url, data=data).json()
            if not response.get("success"):
                verified = False
        if verified:
            return super().form_valid(form)
        return super().form_invalid(form)



# logout view
class LogoutView(auth_views.LogoutView):
    template_name = "registration/logged_out.html"


# password reset
class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    from_email = None
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("core:password_reset_done")
    template_name = "registration/password_reset_form.html"


# password reset done view
class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


# password reset confirm view
class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy("core:password_reset_complete")
    template_name = "registration/password_reset_confirm.html"


# Product Create View
class ProductCreateView(
    auth_mixins.LoginRequiredMixin, SuccessMessageMixin, views.CreateView
):
    template_name = "core/product/create.html"
    model = core_models.ProductModel
    form_class = core_forms.ProductForm
    permission_required = "product.add"
    permission_denied_message = "You don't have the permission!"
    success_message = "Product created successfully!"
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    


# productlist view
class ProductListView(views.ListView):
    template_name = "shop/product_list.html"
    model = core_models.ProductModel
    paginate_by = 20
    context_object_name = "products"


# product details View
class ProductDetailView(views.DetailView):
    template_name = "shop/product_detail.html"
    model = core_models.ProductModel
    context_object_name = "product"


# categorylist view
class CategoryListView(views.ListView):
    template_name = "shop/category_list.html"
    model = core_models.CategoryModel
    paginate_by = 20
    paginate_by = 20
    context_object_name = "categories"


# product list by category view
class ProductListByCategory(views.ListView):
    template_name = "shop/shop.html"
    model = core_models.ProductModel
    paginate_by = 5
    context_object_name = "products"

    def get_queryset(self):
        qs = super().get_queryset()
        pk = int(self.kwargs.get("pk"))
        qs = qs.filter(category__id=pk)
        return qs


# cart view
class CartView(views.TemplateView):
    template_name = "shop/cart.html"
    form_class = core_forms.CartItemFormSet
    model = core_models.CartItemModel
    # currency_form = CurrencyForm

    def get(self, request):
        cart = core_models.CartModel.get_cart(request)
        cart_items = cart.items()
        form = self.form_class(queryset=cart_items)
        context = {
            "form": form,
            # "currency_form": self.currency_form(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        cart = core_models.CartModel.get_cart(request)
        cart_items = cart.items()
        form = self.form_class(request.POST, initial=cart_items)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):

        # currency_form = self.currency_form(self.request.POST)
        # if currency_form.is_valid():
        # currency = currency_form.cleaned_data.get("currency")

        # self.request.session["currency"] = currency or None

        form.save()

        messages.success(self.request, "Cart updated successfully!")

        url = self.request.META.get("HTTP_REFERER")
        return redirect(url)

    def form_invalid(self, form):
        context = {"formset": form}
        messages.error(self.request, "Cart updation failed!")
        return render(self.request, self.template_name, context)


# add item to cart
class AddToCartView(auth_mixins.LoginRequiredMixin, views.TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("pk")
            product = core_models.ProductModel.objects.get(id=pk)

            cart = core_models.CartModel.get_cart(request)

            cart_item, created = core_models.CartItemModel.objects.get_or_create(
                cart=cart,
                product=product,
            )

            if created:
                cart_item.quantity = 1
            else:
                cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Added!")

        except:
            messages.error(request, "Something went wrong!")

        url = request.META.get("HTTP_REFERER")
        return redirect(url)


# checkout view
class CheckoutView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "shop/checkout.html"
    billing_address_form = core_forms.BillingAddressForm
    shipping_address_form = core_forms.ShippingAddressForm

    def get(self, request):
        address = None
        address = request.user.profilemodel.addresses.first() or None

        context = {
            "billing_form": self.billing_address_form(instance=address),
            "shipping_form": self.shipping_address_form(),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        same_as_billing_address = request.POST.get("same_as_billing_address", None)
        billing_form = shipping_form = self.billing_address_form(request.POST)

        if not same_as_billing_address:
            shipping_form = self.shipping_address_form(request.POST)

        if billing_form.is_valid() and shipping_form.is_valid():
            return self.form_valid(billing_form, shipping_form)

        return self.form_invalid(billing_form, shipping_form)

    def apply_other_charges(self, amount):
        cost = amount + 0
        return cost

    def get_delivery_charge(self, shipping_address):
        cost = 0
        return cost

    def form_valid(self, billing_form, shipping_form):
        currency = "INR"
        cart = core_models.CartModel.get_cart(self.request)
        billing_address = billing_form.save()
        shipping_address = shipping_form.save()
        delivery_charge = self.get_delivery_charge(shipping_address)
        amount = self.apply_other_charges(cart.total() + delivery_charge) * 100

        # create order
        data = {
            "amount": amount,
            "currency": currency,
            "payment_capture": 0,
        }
        razorpay_order = RAZORPAY_CLIENT.order.create(data=data)
        id = razorpay_order.get("id", None)

        core_models.OrderModel.objects.create(
            id=id,
            cart=cart,
            amount=amount,
            delivery_charge=delivery_charge,
            billing_address=billing_address,
            shipping_address=shipping_address,
        )

        return redirect(reverse_lazy("core:payment_handler"))

    def form_invalid(self, billing_form, shipping_form):
        context = {
            "billing_form": billing_form,
            "shipping_form": shipping_form,
        }
        return render(self.request, self.template_name, context)


# order view
class OrderView(auth_mixins.LoginRequiredMixin, views.ListView):
    template_name = "shop/order.html"
    model = core_models.OrderModel
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(cart__user=user)
        return qs


# Order detail
class OrderDetailView(auth_mixins.LoginRequiredMixin, views.DetailView):
    template_name = "shop/product_detail.html"
    model = core_models.OrderModel
    context_object_name = "order"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(cart__user=user)
        return qs


# Order history
class OrderHistoryView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "shop/order_history.html"
    model = core_models.OrderModel

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        user = self.request.user
        orders = core_models.OrderModel.objects.filter(cart__user=user)
        context = {"orders": orders}
        context.update(kwargs)
        return context


# Wishlist Create view
class WishlistCreateView(views.CreateView):
    template_name = "shop/wishlist_create.html"
    model = core_models.WishlistModel
    form_class = core_forms.WishlistForm
    # success_url = reverse_lazy("core:wishlist_list")

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        return super().form_valid(form)


# Wishlist listing view
class WishlistListView(views.ListView):
    template_name = "shop/wishlist_list.html"
    context_object_name = "wishlists"
    model = core_models.WishlistModel

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(status=True, user=user)
        return qs


# Wishlist detail view
class WishlistDetailView(views.DetailView):
    template_name = "shop/wishlist_detail.html"
    context_object_name = "wishlist"
    model = core_models.WishlistModel
    extra_context = {
        "wishlist_action": "remove from",
        "wishlist_action_link": "remove_from_wishlist",
    }


# add to wishlist view
class AddToWishlist(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "shop/wishlist_add.html"
    wishlist_model = core_models.WishlistModel
    product_model = core_models.ProductModel
    add_to_wishlist_form = core_forms.AddToWishlistFormSet

    def get(self, request, **kwargs):
        user = request.user
        wishlists = self.wishlist_model.objects.filter(status=True, user=user)
        product_id = kwargs.get("product_pk", None)
        product = None
        try:
            product = self.product_model.objects.get(id=product_id)
        except:
            pass

        context = {
            "product": product,
            "form": self.add_to_wishlist_form(),
            "wishlists": wishlists,
            "wishlist_action": "add to",
        }

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):

        product_id = kwargs.get("product_pk", None)
        wishlist_ids = request.POST.getlist("wishlists")
        try:
            product = self.product_model.objects.get(id=product_id)
            wishlists = [
                wishlist
                for wishlist in self.wishlist_model.objects.filter(id__in=wishlist_ids)
            ]
            product.wishlistmodel_set.set(wishlists)
            messages.success(request, f"{product} Updated successfully!")
        except Exception as e:
            messages.error(request, f"Something is went wrong! ERROR: {e}")

        url = self.request.META.get("HTTP_REFERER")
        return redirect(url)


# Remove product from wishlist
class RemoveFromWishlistView(views.UpdateView):
    def post(self, request, **kwargs):
        product_id = kwargs.get("product_id", None)
        wishlist_id = request.POST.get("wishlist_id", None)

        try:
            wishlist = core_models.WishlistModel.objects.get(id=wishlist_id)
            wishlist.products.remove(product_id)
            wishlist.save()
            messages.success(request, "Product removed from wishlist successfully!")
        except:
            messages.error(request, "Sorry, Can not remove product from wishlist!")

        url = self.request.META.get("HTTP_REFERER")
        return redirect(url)


# Product Review add view
class ProductReviewAddView(auth_mixins.LoginRequiredMixin, views.View):
    template_name = "shop/product_review_add.html"
    form_class = core_forms.ProductReviewForm
    success_url = reverse_lazy("core:shop")

    def get(self, request, **kwargs):
        product_id = kwargs.get("pk")
        product = core_models.ProductModel.objects.filter(id=product_id).first()

        context = {"form": self.form_class(), "product": product}

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        try:
            user = self.request.user
            product_id = self.kwargs.get("pk")
            product = core_models.ProductModel.objects.get(id=product_id)
            form.instance.user = user
            form.instance.product = product
            form.save()
            messages.success(self.request, "Review added successfully!")
        except:
            messages.error(self.request, "Sorry! Could't add review!")
            return self.form_invalid(form)
        return redirect(self.success_url)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})


# Payment List view
class PaymentListView(auth_mixins.LoginRequiredMixin, views.ListView):
    template_name = "core/payment_list.html"
    model = core_models.PaymentModel
    context_object_name = "payments"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(order__cart__user=user)
        return qs
