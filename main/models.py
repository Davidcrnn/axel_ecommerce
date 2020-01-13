from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField
# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.FloatField()
    color = models.CharField(max_length=100)
    size = models.CharField(max_length=15)
    quantity = models.IntegerField(default=1)
    visible_home = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)
    slug = models.CharField(max_length=200, unique=True)
    image1 = models.FileField(upload_to='images/', null=True, blank=True)
    image2 = models.FileField(upload_to='images/', null=True, blank=True)
    image3 = models.FileField(upload_to='images/', null=True, blank=True)

    class Meta:
        """Meta definition for Product."""

        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove-from-cart', kwargs={'slug': self.slug})


class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name

    def get_total_product_price(self):
        return self.product.quantity * self.product.price


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    ordered = models.BooleanField(default=False)
    information = models.ForeignKey(
        'Information', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Commande de {self.user.username}"

    def get_total(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_total_product_price()

        return total


class Information(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    phone = models.IntegerField()
    email = models.EmailField()
    adresse = models.CharField(max_length=60)
    code_postal = models.IntegerField()
    pays = CountryField(multiple=False)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
