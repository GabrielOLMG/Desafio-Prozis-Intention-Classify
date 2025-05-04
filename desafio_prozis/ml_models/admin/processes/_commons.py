from django.contrib import admin


class StandardProcessAdmin(admin.ModelAdmin):
    """
    Classe Geral Para Processos Celery.
    """

    list_display = [
        "current_action",
        "last_action",
        "celery_running",
        "celery_status",
        "started",
        "finished",
    ]

    readonly_fields = list_display
    actions = ["kill_celery"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # ----------------------------------------------- #
    # --------------------Actions-------------------- #
    # ----------------------------------------------- #

    @admin.action(
        description="EXTRA. Finalizar Celery",
    )
    def kill_celery(self, request, queryset):
        for obj in queryset:
            obj.kill_celery()
