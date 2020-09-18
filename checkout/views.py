from django.shortcuts import render, redirect, reverse
from .forms import OrderForm
from django.contrib import messages
from django.conf import settings
from bag.context import bag_contents
import stripe


# Create your views here.
def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bagat the moment.")
        return redirect(reverse('products'))

    order_form = OrderForm()
    id_stripe_public_key = settings.STRIPE_PUBLIC_KEY

    if not id_stripe_public_key:
        messages.warning(request,
                         "Stripe public key is missing.\
                              Did you forget to add it?")

    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    stripe_total = round(total * 100)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,)
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'id_stripe_public_key': id_stripe_public_key,
        'id_client_secret': intent.client_secret,
    }
    return render(request, template, context)
