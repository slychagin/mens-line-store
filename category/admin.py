from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("category_name",)}
    list_display = ('category_name', 'slug')
    search_fields = ('category_name',)
    list_per_page = 20
    list_max_show_all = 100


admin.site.register(Category, CategoryAdmin)
