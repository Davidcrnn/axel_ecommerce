from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from .models import Product, OrderProduct, Order, Information, Payment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.conf import settings
from .forms import CheckoutForm

import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


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

            # order_product.save()

            messages.info(
                request, 'Cet article est déjà dans votre panier. Vous ne pouvez pas en commander plus de 1')
            return redirect("products")
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


@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            order.products.remove(order_product)
            messages.info(request, 'Le produit a été supprimé du panier')
            return redirect("products")
        else:
            messages.info(request, "Le produit n'est pas dans votre panier")
            return redirect('products')
    else:
        messages.info(request, "Vous n'avez pas de commande")
        return redirect('products')
    return redirect('products')


class CheckoutView(View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect('checkout')

        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(
                user=self.request.user, ordered=False)
            if form.is_valid():
                print('Form valid')
                nom = form.cleaned_data.get('name')
                prenom = form.cleaned_data.get('prenom')
                phone = form.cleaned_data.get('phone')
                adresse = form.cleaned_data.get('adresse')
                code_postal = form.cleaned_data.get('code_postal')
                email = form.cleaned_data.get('email')
                pays = form.cleaned_data.get('pays')

                if is_valid_form([nom, prenom, adresse]):
                    adresse_info = Information(
                        user=self.request.user,
                        nom=nom,
                        prenom=prenom,
                        pays=pays,
                        adresse=adresse,
                        code_postal=code_postal,
                        phone=phone,
                        email=email
                    )
                    adresse_info.save()

                    order.information = adresse_info
                    order.save()

            messages.info(
                self.request, 'Les informations ont bien été prises en compte')
            return redirect('payment')

        except ObjectDoesNotExist:
            messages.info(self.request, 'This order does not exist.')
            return redirect('request-refund')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        print(order.information)
        if order.information:

            context = {
                'order': order,
            }
            return render(self.request, 'payment.html', context)
        else:
            messages.warning(
                self.request, "Vous devez remplir le formulaire avant d'accèder au paiement ")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        print(token)
        amount = int(order.get_total())

        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),
                currency='eur',
                # replace by token in prod 'tok_visa'
                source='tok_visa',
            )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = amount
            payment.save()

            order_items = order.products.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(
                self.request, "Votre commande a bien été prise en compte!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")
