from django.db import models

from desafio_prozis.core.models import UserIntention


class UnitTest(models.Model):
    text = models.TextField(help_text="Instruction text")
    expected_label = models.ForeignKey(
        UserIntention,
        on_delete=models.CASCADE,
        related_name="expected_unit_tests",
        help_text="Label Expected",
    )
    predicted_label = models.ForeignKey(
        UserIntention,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="predicted_unit_tests",
        help_text="Predicted label",
    )

    custom_test = models.BooleanField(
        default=False,
        help_text="whether it is a test created by prozis or not",
    )

    class Meta:
        db_table = "unit_test"
        verbose_name = "Unit Test"
        verbose_name_plural = "Unit Tests"
        unique_together = ("text", "expected_label")

    def __str__(self):
        return f"Unit Test: {self.text} -> {self.expected_label}"

    def is_correct(self):
        return self.predicted_label == self.expected_label
