from django.db import models


class UserIntention(models.Model):
    text = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "user_intention"
        verbose_name = "User Intention"
        verbose_name_plural = "User Intentions"

    def __str__(self):
        return self.text
