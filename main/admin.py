from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Product)
admin.site.register(models.OrderProduct)
admin.site.register(models.Order)
admin.site.register(models.Payment)
admin.site.register(models.Information)
