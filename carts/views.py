from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product, Variation


def _cart_id(request):
    """
    Get the cart by session_key present in the session
    :param request:
    :return: cart by particular session key
    """
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    """
    Add the particular product to the cart by product id.
    :param request:
    :param product_id: id of the product we want to add to the cart
    :return: redirect user to 'cart' page
    """
    product = Product.objects.get(id=product_id)  # get the product
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                  variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
    except ObjectDoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except ObjectDoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
    return redirect('cart')


def remove_cart(request, product_id):
    """
    Pressing the minus button decreases the quantity of product by one.
    :param request:
    :param product_id:
    :return: render cart page with new quantity
    """
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id):
    """
    Pressing the remove button delete product from cart.
    :param request:
    :param product_id:
    :return: render cart page with new list of products
    """
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


def cart_page(request, total=0, quantity=0, cart_items=None, discount=0, grand_total=0):
    """
    This function render 'cart' page and calculate total sum, quantity, discount and grand total sum.
    :param request:
    :param total: Sum without discount in present time
    :param quantity: Product quantity in present time
    :param cart_items: Products in cart
    :param discount: Discount sum
    :param grand_total: Amount including discount
    :return: render 'cart' page
    """
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        if total < 5000:
            discount = round(total * 0.03)
        else:
            discount = round(total * 0.07)
        grand_total = total - discount
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'discount': discount,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)
