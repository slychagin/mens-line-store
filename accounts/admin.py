from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from . models import Account, UserProfile


class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ['-date_joined']
    list_per_page = 20
    list_max_show_all = 100

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(obj.profile_picture.url))
    thumbnail.short_description = 'Фото профиля'
    list_display = ('thumbnail', 'user', 'city', 'region', 'country')
    list_display_links = ('user', 'thumbnail')
    list_per_page = 20
    list_max_show_all = 100


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
