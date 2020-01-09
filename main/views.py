from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from .models import Product, OrderProduct, Order
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


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


class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order-summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Votre panier est vide")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_product, created = OrderProduct.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__slug=product.slug).exists():

            order_product.save()
            messages.info(
                request, 'La quantité du produit a été ajouté au panier')
            return redirect("order-summary")
        else:
            messages.info(request, 'Le produit a été ajouté au panier')
            order.products.add(order_product)
            return redirect("products")
    else:

        order = Order.objects.create(
            user=request.user)
        order.products.add(order_product)
        messages.info(request, 'Le produit a été ajouté au panier')
    return redirect("products")
