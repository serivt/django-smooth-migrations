from django.core.management.base import BaseCommand

from smooth_migrations.context import MigrationContext


class Command(BaseCommand):
    help: str = (
        "Applies all pending migrations and, if an error occurs, rolls back to the last migration applied at the time"
        " of command execution."
    )

    def handle(self, *args, **options):
        self._show("New fields:", MigrationContext.new_fields)
        self._show(
            "Backward compatbile models:", MigrationContext.backward_compatible_models
        )
        self._show("Deprecated fields:", MigrationContext.deprecated_fields)
        self._show("Deprecated models:", MigrationContext.deprecated_models)

    def _show(self, title: str, context: list) -> None:
        if not context:
            return
        self.stdout.write(self.style.MIGRATE_HEADING(title))
        for item in context:
            self.stdout.write(f"  {item}")
