from .models import Category


def menu_links(request):
    """
    Get links for all categories in database.
    After that we can use this links in templates (navbar e.g.)
    :param request:
    :return: dictionary of links
    """
    links = Category.objects.all()
    return dict(links=links)
