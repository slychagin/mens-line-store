from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q, Max, Min
from django.db.models.functions import Lower
from django.shortcuts import render, get_object_or_404, redirect
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from orders.models import OrderProduct
from .forms import ReviewForm
from .models import Product, ReviewRating, ProductGallery


def paginator(request, product_list, products_per_page):
    """
    Paginate pages in the store
    :param request:
    :param product_list: List of all products in the store or in the category
    :param products_per_page: How many products per page show
    :return: Number of products displayed
    """
    product_paginator = Paginator(product_list, products_per_page)
    page = request.GET.get('page')
    paged_products = product_paginator.get_page(page)
    return paged_products


def store(request, category_slug=None):
    """
    Render 'store' page where show all products or products by category in sale.
    :param request:
    :param category_slug: Category name
    :return: Render store.html
    """
    categories = None
    products = None

    # Sidebar panel (products amount, price range)
    all_products_count = Product.objects.all().count()
    max_price_placeholder = Product.objects.aggregate(Max('price'))['price__max']
    min_price_placeholder = Product.objects.aggregate(Min('price'))['price__min']

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        if 'min_price' in request.GET:
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')
            if min_price == '':
                min_price = 0
            if max_price == '':
                max_price = Product.objects.aggregate(Max('price'))['price__max']
            products = Product.objects.filter(price__range=(min_price, max_price), category=categories, is_available=True).order_by('id')
            paged_products = paginator(request, products, 6)
            product_count = products.count()
        else:
            products = Product.objects.filter(category=categories, is_available=True).order_by('id')
            paged_products = paginator(request, products, 6)
            product_count = products.count()
    else:
        if 'min_price' in request.GET:
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')
            if min_price == '':
                min_price = 0
            if max_price == '':
                max_price = Product.objects.aggregate(Max('price'))['price__max']
            products = Product.objects.all().filter(is_available=True, price__range=(min_price, max_price)).order_by('id')
            paged_products = paginator(request, products, 6)
            product_count = products.count()
        else:
            products = Product.objects.all().filter(is_available=True).order_by('id')
            paged_products = paginator(request, products, 6)
            product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'all_products_count': all_products_count,
        'max_price_placeholder': max_price_placeholder,
        'min_price_placeholder': min_price_placeholder
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except ObjectDoesNotExist:
            order_product = None
    else:
        order_product = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'order_product': order_product,
        'reviews': reviews,
        'product_gallery': product_gallery
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    """
    Find products by keyword
    :param request:
    :return: Render 'store' page
    """
    products = None
    paged_products = None
    product_count = None
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by(
                '-created_date').filter(Q(product_name__icontains=keyword) |
                                        Q(description__icontains=keyword))
            if 'keyword' in request.GET and request.GET['keyword']:
                page = request.GET.get('page')
                keyword = request.GET['keyword']
                paginator = Paginator(products, 6)
            paged_products = paginator.get_page(page)
            product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'keyword': keyword
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Спасибо! Ваш отзыв обновлен.')
            return redirect(url)
        except ObjectDoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Спасибо! Ваш отзыв отправлен.')
                return redirect(url)
