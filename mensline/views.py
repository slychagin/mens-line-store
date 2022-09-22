from django.shortcuts import render

from slider.models import Slider
from store.models import Product, ReviewRating


def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('-created_date')

    # Get the reviews
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    # Get photos for slider
    slider_list = Slider.objects.all()

    context = {
        'products': products,
        'reviews': reviews,
        'slider_list': slider_list
    }
    return render(request, 'home.html', context)
