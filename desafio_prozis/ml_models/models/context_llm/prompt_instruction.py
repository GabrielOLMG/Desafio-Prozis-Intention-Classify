from django.db import models


class PromptInstruction(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordem da instrução no prompt",
    )
    text = models.TextField(help_text="Texto da instrução")

    class Meta:
        ordering = ("order",)
        db_table = "llm_prompt_instructions"
        verbose_name = "Prompt Instruction"
        verbose_name_plural = "Prompt Instructions"

    def __str__(self):
        return f"Prompt Instruction {self.order}"
