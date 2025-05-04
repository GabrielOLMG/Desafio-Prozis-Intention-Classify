from django.contrib import admin

from desafio_prozis.ml_models.admin.processes._commons import StandardProcessAdmin
from desafio_prozis.ml_models.models import UnitTestProcess


@admin.register(UnitTestProcess)
class UnitTestProcessAdmin(StandardProcessAdmin):
    list_display = ["id", *StandardProcessAdmin.list_display]

    actions = ["process_unit_test", *StandardProcessAdmin.actions]

    @admin.action(
        description="1. Executar Processos Unitarios",
    )
    def process_unit_test(self, request, queryset):
        for obj in queryset:
            obj.process_unit_test()
