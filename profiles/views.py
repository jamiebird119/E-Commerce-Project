from django.shortcuts import render, get_object_or_404
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib import messages
from checkout.models import Order


# Create your views here.
def profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Successfully updated delivery information.')
        else:
            messages.error(request, 'Failed to update/add user information. Please ensure form is valid')
    else:
        template = 'profiles/profile.html'
        form = UserProfileForm(instance=profile)
        orders = profile.orders.all()
        context = {
            'form': form,
            'orders': orders,
            'on_profiles_page': True,
        }
        return render(request, template, context)


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    messages.info(request,
                  (f'This is a past order confirmation for order number {order_number}.'
                   'A confirmation email was sent on the order date'
                   ))
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }
    return render(request, template, context)
