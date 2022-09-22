from django.contrib import admin
from django.utils.html import format_html

from slider.models import Slider


class SliderAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        return format_html('<img src="{}" width="120" height="40"">'.format(obj.slider_image.url))

    thumbnail.short_description = 'Фото'
    list_display = ('slider_title', 'thumbnail', 'slider_css',)


admin.site.register(Slider, SliderAdmin)
