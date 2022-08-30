from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from .models import Product


def store(request, category_slug=None):
    """
    Render 'store' page where show all products or products by category in sale.
    :param request:
    :param category_slug: Category name
    :return: Render store.html
    """
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paged_products = paginator(request, products, 1)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paged_products = paginator(request, products, 3)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)


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


def search(request):
    """
    Find products by keyword
    :param request:
    :return: Render 'store' page
    """
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        products = Product.objects.order_by('-created_date').filter(
            Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
        product_count = products.count()
        if not keyword:
            products = ''
            product_count = 0
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)
