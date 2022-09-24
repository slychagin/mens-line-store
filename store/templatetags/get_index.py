from django import template


register = template.Library()


@register.filter(name='get_index')
def get_index(my_list, i):
    return my_list[i]
