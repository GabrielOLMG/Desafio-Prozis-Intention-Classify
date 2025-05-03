from django.contrib import admin

from desafio_prozis.core.models import UserIntention


@admin.register(UserIntention)
class UserIntentionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "ml_text")
