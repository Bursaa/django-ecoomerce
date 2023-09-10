from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, null=True)
    allegro_id = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=200, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    allegro_id = models.IntegerField(null=True)

    def __str__(self):
        if self.category:
            return self.category.name + "/" + self.name
        else:
            return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=200, null=True, default=user.name)
    email = models.EmailField(max_length=200, null=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)

    def __str__(self):
        try:
            return self.phone_number + "-" + self.email
        except:
            return self.email


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    max_quantity = models.IntegerField(null=True, blank=True, default=1)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, blank=True, null=True)

    ACTION_CHOICES = (
        ('change', 'Change'),
        ('add', 'Add'),
        ('delete', 'Delete'),
        ('no_action', 'No Action'),
    )

    allegro_action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        default='no_action',  # Domyślna wartość to 'no_action'
    )
    allegro_offer_id = models.CharField(
        max_length=20,
        default='not added',
    )

    olx_action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        default='no_action',  # Domyślna wartość to 'no_action'
    )
    olx_offer_id = models.CharField(
        max_length=10,
        default='not added',
    )

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = '/images/placeholder.png'
        return url

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.subcategory:
            self.category = self.subcategory.category
        elif not self.category:
            default_category, created = Category.objects.get_or_create(name='Inne')
            self.category = default_category
        super().save(*args, **kwargs)


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.customer)+" - "+str(self.date_ordered) + " - " + str(self.complete)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        cart_total = sum([item.get_total for item in orderitems])
        return cart_total

    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        cart_items = sum([item.quantity for item in orderitems])
        return cart_items


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        try:
            return self.order.transaction_id + " - " + self.product.name
        except:
            return "Zamówienie nie dokończone"


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class Token(models.Model):
    name = models.CharField(max_length=40)
    access_token = models.CharField(max_length=5000, default="", blank=True, null=True)
    refresh_token = models.CharField(max_length=5000, default="", blank=True, null=True)
    time_of_invalidation = models.DateTimeField(default=None, blank=True, null=True)
    authorized = models.BooleanField(default=False)

    def __str__(self):
        return self.name