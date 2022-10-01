from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    search_fields = ('product_name', 'category__category_name')
    list_per_page = 20
    list_max_show_all = 100
    prepopulated_fields = {"slug": ("product_name",)}
    inlines = [ProductGalleryInline]


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')
    search_fields = ('product__product_name',)
    list_per_page = 50
    list_max_show_all = 100


class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'subject', 'rating', 'status', 'created_at')
    search_fields = ('product__product_name',)
    list_per_page = 20
    list_max_show_all = 100


class ProductGalleryAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        return format_html('<img src="{}" width="40"">'.format(obj.image.url))

    thumbnail.short_description = 'Фото товара'
    list_display = ('product', 'thumbnail')
    list_display_links = ('product', 'thumbnail')
    list_filter = ('product',)
    search_fields = ('product__product_name',)
    list_per_page = 20
    list_max_show_all = 100


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)
admin.site.register(ProductGallery, ProductGalleryAdmin)
