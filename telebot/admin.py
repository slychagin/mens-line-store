from django.contrib import admin
from telebot.models import TeleSettings


class TeleSettingsAdmin(admin.ModelAdmin):
    list_display = ('tg_chat', 'tg_message')


admin.site.register(TeleSettings, TeleSettingsAdmin)
