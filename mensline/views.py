from django.db.models import Count
from django.shortcuts import render, redirect
from orders.models import OrderProduct
from slider.models import Slider
from store.models import Product, ReviewRating


def home(request):
    # Get photos for slider
    slider_list = Slider.objects.all()

    # Get most popular products
    filtered_products = (OrderProduct.objects.values('product_id').
                         annotate(product_count=Count('product_id')).
                         order_by('-product_count')[:8])

    most_popular_products = [Product.objects.get(id=product['product_id']) for product in filtered_products]

    # Get the reviews
    reviews = None
    for product in most_popular_products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'most_popular_products': most_popular_products,
        'reviews': reviews,
        'slider_list': slider_list
    }
    return render(request, 'home.html', context)
