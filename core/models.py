from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q, Sum
from django.urls import reverse
from core import models as core_models


class User(AbstractUser):
    def has_profile(self):
        profile = getattr(self, "profilemodel", None)
        return profile


USER = settings.AUTH_USER_MODEL

# Abstract models
class TimeStamp(models.Model):
    status = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# location model
class LocationModel(TimeStamp, models.Model):
    longitude = models.FloatField()
    lattitude = models.FloatField()

    def __str__(self):
        return f"{self.longitude},{self.lattitude}"


# address model
class AddressModel(TimeStamp, models.Model):
    building_name = models.CharField(max_length=120)
    place = models.CharField(max_length=64)
    street = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    district = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    post_office = models.CharField(max_length=64)
    post_code = models.CharField(max_length=64)
    location = models.ForeignKey(
        "LocationModel", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.building_name}\n{self.place}\n{self.district}\n{self.state} - {self.post_code}"

    def get_absolute_url(self):
        return reverse("core:address_detail", kwargs={"pk": self.pk})


# contact model
class FeedbackModel(TimeStamp, models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)
    subject = models.CharField(max_length=120, default="I want to know more.")
    message = models.TextField(max_length=500)
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class FeedbackReplyModel(TimeStamp, models.Model):
    feedback = models.OneToOneField("FeedbackModel", on_delete=models.CASCADE)
    reply = models.TextField(max_length=500)
    user = models.ForeignKey(USER, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.feedback.subject}"


# profile model
class ProfileModel(TimeStamp, models.Model):
    class GenderChoices:
        male = "m"
        female = "f"
        transgender = "t"

    class AccountTypeChoices:
        customer = "customer"
        administrator = "admin"
        merchant = "merchant"

    GENDER_CHOICES = (
        ("Male", GenderChoices.male),
        ("Female", GenderChoices.female),
        ("Transgender", GenderChoices.transgender),
    )

    ACCOUNT_TYPE_CHOICES = (
        ("Customer", AccountTypeChoices.customer),
        ("Merchant", AccountTypeChoices.merchant),
        ("Administrator", AccountTypeChoices.administrator),
    )

    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    gender = models.CharField(max_length=12, choices=GENDER_CHOICES)
    addresses = models.ManyToManyField("AddressModel")
    
    image = models.ImageField(
        upload_to="user/profile/image", default="default/user.png"
    )

    account_type = models.CharField(
        max_length=16,
        choices=ACCOUNT_TYPE_CHOICES,
        default=AccountTypeChoices.customer,
    )
    user = models.OneToOneField(USER, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_loyal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("core:profile_detail", kwargs={"pk": self.pk})
    

    


# Shopping models ================================================

# unit model
class UnitModel(core_models.TimeStamp, models.Model):
    name = models.CharField(max_length=16)
    symbol = models.CharField(max_length=16)
    convertion_rate = models.FloatField()
    secondary = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("core:unit_detail", kwargs={"pk": self.pk})


# category model
class CategoryModel(core_models.TimeStamp, models.Model):
    name = models.CharField(max_length=48)
    image = models.ImageField(
        upload_to="category/image/", default="default/category.png"
    )
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("core:category_detail", kwargs={"pk": self.pk})


# product model
class ProductModel(core_models.TimeStamp, models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(max_length=500)
    price = models.FloatField()
    image = models.ImageField(upload_to="product/image/", default="default/product.png")
    category = models.ForeignKey(
        "CategoryModel", on_delete=models.SET_NULL, null=True, blank=True
    )

    unit = models.ForeignKey(
        "UnitModel", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("core:product_detail", kwargs={"pk": self.pk})


# cart model
class CartModel(core_models.TimeStamp, models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE)
    empty = models.BooleanField(default=True)
    checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"

    def get_absolute_url(self):
        return reverse("core:cart_detail", kwargs={"pk": self.pk})

    def total(self):
        price = (
            (
                CartItemModel.objects.filter(cart=self, status=True).annotate(
                    item_price=F("quantity") * F("product__price")
                )
            )
            .aggregate(Sum("item_price"))
            .get("item_price__sum")
        )

        return price

    def items(self):
        cart_items = CartItemModel.objects.filter(cart__user=self.user, status=True)
        return cart_items

    @staticmethod
    def get_cart(request, **kwargs):
        user = request.user
        cart, created = CartModel.objects.get_or_create(
            user=user,
            status=True,
            checked_out=False,
            **kwargs,
        )
        return cart


# cartitem model
class CartItemModel(core_models.TimeStamp, models.Model):
    cart = models.ForeignKey("CartModel", on_delete=models.CASCADE)
    product = models.ForeignKey("ProductModel", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} ({self.quantity})"

    def get_absolute_url(self):
        return reverse("core:cart_item_detail", kwargs={"pk": self.pk})

    def total(self):
        cost = self.product.price * self.quantity
        return cost


# wishlist model
class WishlistModel(TimeStamp, models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(max_length=500, blank=True, default="")
    products = models.ManyToManyField("ProductModel", blank=True)
    user = models.ForeignKey(USER, on_delete=models.CASCADE, blank=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("core:wishlist_detail", kwargs={"pk": self.pk})


class ReviewModel(TimeStamp, models.Model):
    product = models.ForeignKey("ProductModel", on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField(max_length=250)
    user = models.ForeignKey(USER, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user} ({self.rating})"

    def get_absolute_url(self):
        return reverse("core:product_review_detail", kwargs={"pk": self.pk})


# order model
class OrderModel(TimeStamp, models.Model):
    class CurrencyChoices:
        INR = "INR"
        DOLLAR = "D"

    CURRENCY_CHOICES = (
        ("Indian Rupee", CurrencyChoices.INR),
        ("Dollar", CurrencyChoices.DOLLAR),
    )

    id = models.CharField(primary_key=True, unique=True, max_length=120)
    cart = models.ForeignKey("CartModel", on_delete=models.CASCADE)
    amount = models.FloatField()
    currency = models.CharField(
        max_length=24,
        choices=CURRENCY_CHOICES,
        default=CurrencyChoices.INR,
    )
    delivery_charge = models.FloatField(default=0)
    completed = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        "AddressModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checkout_billing_address",
    )
    shipping_address = models.ForeignKey(
        "AddressModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checkout_shipping_address",
    )

    def __str__(self) -> str:
        return f"{self.id or self.cart} {'Completed' if self.completed else 'Not Completed'}"

    def get_absolute_url(self):
        return reverse("core:order_detail", kwargs={"pk": self.pk})

    def total(self):
        cart_total = self.cart.total
        cost = cart_total + self.delivery_charge
        return cost


# payment model
class PaymentModel(TimeStamp, models.Model):
    class PaymentStatusChoices:
        pending = "pending"
        completed = "completed"
        failed = "failed"

    PAYMENT_STATUS_CHOICES = (
        ("Pending", PaymentStatusChoices.pending),
        ("Completed", PaymentStatusChoices.completed),
        ("Failed", PaymentStatusChoices.failed),
    )

    id = models.CharField(primary_key=True, unique=True, max_length=120)
    order = models.ForeignKey(
        "OrderModel", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=16,
        choices=PAYMENT_STATUS_CHOICES,
        default=PaymentStatusChoices.pending,
    )
    mode = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.status}"

    def get_absolute_url(self):
        return reverse("core:payment_detail", kwargs={"pk": self.pk})
