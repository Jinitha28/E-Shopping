from django import forms
from django.contrib import auth
from django.contrib.auth import forms as auth_forms

from core import models as core_models

USER = auth.get_user_model()


class AddressForm(forms.ModelForm):
    class Meta:
        model = core_models.AddressModel
        exclude = (
            "location",
            "status",
            "created_on",
            "updated_on",
        )


# Profile form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = core_models.ProfileModel
        exclude = (
            "status",
            "location",
            "address",
            "user",
            "is_loyal",
            "is_active",
            "account_type",
        )


# feedback form
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = core_models.FeedbackModel
        exclude = ("is_replied", "status", "user")


# cartitem form
class CartItemForm(forms.ModelForm):
    class Meta:
        model = core_models.CartItemModel
        fields = ["product", "quantity"]


CartItemFormSet = forms.modelformset_factory(
    core_models.CartItemModel,
    form=CartItemForm,
    edit_only=True,
    extra=0,
    can_delete=True,
)

AddressFormSet = forms.modelformset_factory(
    core_models.AddressModel,
    form=AddressForm,
    edit_only=True,
    extra=1,
    can_delete=False,
)


# Billing form
class BillingAddressForm(AddressForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Billing Address"
        self.prefix = "billing"


# shipping form
class ShippingAddressForm(AddressForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Shipping Address"
        self.prefix = "shipping"


# wishlistform
class WishlistForm(forms.ModelForm):
    class Meta:
        model = core_models.WishlistModel
        fields = ["name", "description"]


# Add to cart form
class AddToWishlistForm(forms.ModelForm):
    class Meta:
        model = core_models.WishlistModel
        fields = ["name"]


AddToWishlistFormSet = forms.modelformset_factory(
    core_models.WishlistModel,
    form=AddToWishlistForm,
    edit_only=True,
    extra=0,
    can_delete=True,
)

# registration form
class UserRegistrationForm(auth_forms.UserCreationForm):
    class Meta:
        model = USER
        fields = ["username", "email"]


# Product create form
class ProductForm(forms.ModelForm):
    class Meta:
        model = core_models.ProductModel
        exclude = ("status", "user")


# Product Review form
class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = core_models.ReviewModel
        fields = ["rating", "comment"]
