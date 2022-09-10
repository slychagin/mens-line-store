import json
from datetime import datetime
from django.shortcuts import render, redirect
from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, Payment
from yookassa import Configuration, Payment as PayKassa
from dotenv import load_dotenv
import uuid
import os

load_dotenv(override=True)


# YOOKASSA PAYMENT
yookassa_secret_key = os.environ.get('YOOKASSA_SECRET_KEY')
yookassa_shop_id = os.environ.get('YOOKASSA_SHOP_ID')


def payments(request):
    body = json.loads(request.body)

    # Requesting the current payment status
    transaction_id = body['transID']
    payment_object = PayKassa.find_one(transaction_id)
    payment_data = json.loads(payment_object.json())
    status = payment_data['status']

    order = Order.objects.get(user=request.user, is_ordered=False, order_number=payment_data['metadata']['orderNumber'])
    payment = Payment(
        user=request.user,
        payment_id=payment_data['id'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=payment_data['status']
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()
    return render(request, 'orders/payments.html')


order_number = None


def place_order(request, total=0, quantity=0):
    global order_number
    current_user = request.user

    # If the cart count is less or equal 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    discount = 0
    grand_total = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    if total < 5000:
        discount = round(total * 0.03)
    else:
        discount = round(total * 0.07)
    grand_total = total - discount

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.region = form.cleaned_data['region']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.discount = discount
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            current_date = datetime.now().strftime('%Y%d%m')
            order_number = current_date + '-' + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'discount': discount,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def yookassa_payment(request):
    current_user = request.user
    order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

    Configuration.account_id = yookassa_shop_id
    Configuration.secret_key = yookassa_secret_key

    payment = PayKassa.create(
        {
            'amount': {
                'value': order.order_total,
                'currency': 'RUB'
            },
            'confirmation': {
                'type': 'embedded',
                'return_url': 'http://127.0.0.1:8000/'
            },
            'capture': True,
            'description': f'Заказ №{order_number}',
            'metadata': {
                'orderNumber': order_number
            },
            'receipt': {
                'customer': {
                    'full_name': f'{order.last_name} {order.first_name}',
                    'email': order.email,
                    'phone': order.phone,
                },
            }
        }, uuid.uuid4())

    payment_object = json.loads(payment.json())
    print(payment_object)

    context = {
        'confirmation_token': payment_object['confirmation']['confirmation_token'],
        'transaction_id': payment_object['id'],
        'order_number': order.order_number,
    }
    return render(request, 'orders/yookassa_payment.html', context)
