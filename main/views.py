from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import Product


class HomePage(TemplateView):
    template_name = 'home.html'


class ProductListView(ListView):
    model = Product
    template_name = "products.html"
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.order_by('created')


class ProductDetailView(DetailView):
    template_name = 'product-detail.html'

    def get_object(self):
        slug_ = self.kwargs.get("slug")
        return get_object_or_404(Product, slug=slug_)
