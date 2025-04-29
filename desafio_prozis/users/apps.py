import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "desafio_prozis.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import desafio_prozis.users.signals  # noqa: F401
