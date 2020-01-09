from django.db import models
from django.conf import settings
from django.urls import reverse
# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.FloatField()
    color = models.CharField(max_length=100)
    size = models.CharField(max_length=15)
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

    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={'slug': self.slug})


class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"Commande de {self.user.username}"
