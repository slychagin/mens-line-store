import json
import uuid
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from carts.models import CartItem
from mensline import settings
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderProduct
from yookassa import Configuration, Payment as PayKassa
from store.models import Product
from telebot.sendmessage import send_telegram


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
            current_date = datetime.now().strftime('%Y%m%d')
            order_number = current_date + '-' + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            order_number = order.order_number

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
    global order_number
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    current_user = request.user

    try:
        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        payment = PayKassa.create(
            {
                'amount': {
                    'value': order.order_total,
                    'currency': 'RUB'
                },
                'confirmation': {
                    'type': 'embedded',
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

        context = {
            'confirmation_token': payment_object['confirmation']['confirmation_token'],
            'transaction_id': payment_object['id'],
            'order_number': order.order_number,
        }
        return render(request, 'orders/yookassa_payment.html', context)
    except ObjectDoesNotExist:
        return redirect('yookassa_payment')


def payments(request):
    body = json.loads(request.body)

    # Requesting the current payment status
    transaction_id = body['transID']
    payment_object = PayKassa.find_one(transaction_id)
    payment_data = json.loads(payment_object.json())

    # Store transaction details inside Payment model
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

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.is_ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order received email to customer
    mail_subject = 'Спасибо за Ваш заказ в MensLineStore!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send message to Telegram chat
    send_telegram(order_number=payment_data['metadata']['orderNumber'],
                  total_sum=order.order_total,
                  last_name=request.user.last_name,
                  first_name=request.user.first_name,
                  email=request.user.email,
                  phone_number=request.user.phone_number)

    # Send order number and transaction id back to sendData method via JSONResponse
    data = {
        'order_number': payment_data['metadata']['orderNumber'],
        'transID': payment_data['id']
    }

    return JsonResponse(data)


def order_complete(request):
    order_complete_number = request.GET.get('order_number')
    trans_id = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_complete_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        sub_total = 0
        for i in ordered_products:
            sub_total += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=trans_id)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'trans_id': payment.payment_id,
            'sub_total': sub_total
        }
        return render(request, 'orders/order_complete.html', context)
    except ObjectDoesNotExist:
        return redirect('home')
