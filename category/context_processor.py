from store.models import Product
from .models import Category


def menu_links(request):
    """
    Get links for all categories in database.
    After that we can use this links in templates anywhere in the project.
    :param request:
    :return: dictionary of links
    """
    links = Category.objects.all().order_by('category_name')
    count_products_by_category = [len(Product.objects.filter(category=link, is_available=True)) for link in links]
    return dict(links=links, count_products_by_category=count_products_by_category)
