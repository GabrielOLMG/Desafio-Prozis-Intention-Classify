from django.contrib import admin
from django.core.exceptions import ValidationError
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from desafio_prozis.core.models import UserIntention
from desafio_prozis.ml_models.models import UnitTest


class UnitTestResource(resources.ModelResource):
    imported_names = set()

    class Meta:
        model = UnitTest
        import_id_fields = []  # Usando os campos definidos manualmente
        fields = ("text", "expected_label", "predicted_label", "custom_test")

    def skip_row(self, instance, original, row, import_validation_errors=None):
        existing_combinations = set(
            UnitTest.objects.values_list("text", "expected_label__text"),
        )

        return (instance.text, instance.expected_label.text) in existing_combinations

    def before_import_row(self, row, **kwargs):
        if "label" not in row or "text" not in row:
            text = (
                'The JSON must have the "text" and'
                ' "label" fields, as in the example sent'
            )
            raise ValidationError(text)

        # Limpeza da label
        expected_label = row["label"].strip()

        # Tenta buscar o UserIntention correspondente
        try:
            intention = UserIntention.objects.get(text=expected_label)
        except UserIntention.DoesNotExist as err:
            text = (
                f'UserIntention "{expected_label}" does not exist.'
                f" Create it before importing."
            )
            raise ValidationError(text) from err

        row["expected_label"] = intention.pk


@admin.register(UnitTest)
class UnitTestAdmin(ImportExportModelAdmin):
    resource_class = UnitTestResource
    list_display = (
        "id",
        "text",
        "expected_label",
        "predicted_label",
        "custom_test",
        "is_correct",
    )
