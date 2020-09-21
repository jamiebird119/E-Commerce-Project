from django.http import HttpResponse
from .models import Order, OrderLineItem, Product
import json
import time


class StripeWH_Handler:
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic unknown webhook event from Stripe
        """
        return HttpResponse(
            content=f'Unhandled webhook received:{event["type"]}', status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle a payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bad
        save_info = intent.metadata.save_info
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount/100, 2)
        for field, value in shipping_details:
            if value == "":
                shipping_details.address[field] = None
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name_iexact=shipping_details.name,
                    email_iexact=shipping_details.email,
                    phone_number_iexact=shipping_details.phone_number,
                    country_iexact=shipping_details.addres.country,
                    postcode_iexact=shipping_details.address.postcode,
                    town_or_city_iexact=shipping_details.address.town_or_city,
                    street_address1_iexact=shipping_details.address.street_address1,
                    street_address2_iexact=shipping_details.address.street_address2,
                    county_iexact=shipping_details.address.county,
                    grand_total_iexact=shipping_details.grand_total,
                    original_bag_iexact=bag,
                    stripe_pid_iexact=pid,
                )
                order_exists = True
                break

            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                content=f'Webhook received:{event["type"]} | SUCCESS: Verified order already in database', status=200
            )
        else:
            order = None
            try:
                order = Order.objects.create(
                        full_name=shipping_details.name,
                        email=shipping_details.email,
                        phone_number=shipping_details.phone_number,
                        country=shipping_details.country,
                        postcode=shipping_details.postcode,
                        town_or_city=shipping_details.town_or_city,
                        street_address1=shipping_details.street_address1,
                        street_address2=shipping_details.street_address2,
                        county=shipping_details.county,
                        grand_total=shipping_details.grand_total,
                        original_bag_iexact=bag,
                        stripe_pid_iexact=pid,
                    )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['item_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received:{event["type"]} | ERROR: {e}', status=500
                )
        return HttpResponse(
            content=f'Webhook received:{event["type"]} | SUCCESS: Order created in webhook', status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle a payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Payemnt Failed webhook received:{event["type"]}', status=200
        )
