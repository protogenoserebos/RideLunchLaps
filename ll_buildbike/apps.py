from django.apps import AppConfig


class LlBuildbikeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ll_buildbike"

    def ready(self):
        from . import signals  # noqa
