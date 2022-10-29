from django import forms
from core import models as core_models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.contrib import auth

USER = auth.get_user_model()

from core.models import (
    Address,
    Cart,
    CartItem,
    
)
class AddressForm(forms.ModelForm):
    class Meta:
        model = core_models.Address
        exclude = (
            "location",
            "status",
            "created_on",
            "updated_on",
        )


# Profile form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = core_models.Profile
        exclude = (
            "status",
            "location",
            "address",
            "user",
            "is_loyal",
            "is_active",
            "account_type",
        )

#currency form
class CurrencyForm(forms.Form):
    pass

#feedback form
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = core_models.Feedback
        exclude = ("is_replied", "status", "user")

#cartitem form
class CartItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CartItemForm, self).__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.id:
            self.fields["product"].widget = forms.HiddenInput(attrs={})

    class Meta:
        model = core_models.CartItem
        fields = ["product", "quantity"]

    def clean_product(self):
        instance = getattr(self, "instance", None)
        if instance:
            return instance.product
        else:
            return self.cleaned_data.get("product", None)


CartItemFormSet = forms.modelformset_factory(
    core_models.CartItem, form=CartItemForm, edit_only=True, extra=0, can_delete=True
)

AddressFormSet = forms.modelformset_factory(
    core_models.Address, form=AddressForm, edit_only=True, extra=1, can_delete=False
)


#Billing form
class BillingAddressForm(AddressForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Billing Address"
        self.prefix = "billing"

#shipping form
class ShippingAddressForm(AddressForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Shipping Address"
        self.prefix = "shipping"


#wishlistform
class WishlistForm(forms.ModelForm):
    class Meta:
        model = core_models.WishlistModel
        fields = ["name", "description"]

#Add to cart form
class AddToWishlistForm(forms.ModelForm):
    class Meta:
        model = core_models.WishlistModel
        fields = ["name"]


AddToWishlistFormSet = forms.modelformset_factory(
    core_models.WishlistModel, form=AddToWishlistForm, edit_only=True, extra=0, can_delete=True
)

# registration form
class UserRegistrationForm(auth_forms.UserCreationForm):
    class Meta:
        model = USER
        fields = ["username", "email"]


# Product Review form
class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = core_models.ReviewModel
        fields = ["rating", "comment"]



