from django.contrib import admin

from desafio_prozis.ml_models.models import PromptInstruction


@admin.register(PromptInstruction)
class PromptInstructionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "text")
