from django.core.management import call_command
from django.core.management.commands import migrate
from django.db.migrations.recorder import MigrationRecorder


class Command(migrate.Command):
    help: str = (
        "Applies all pending migrations and, if an error occurs, rolls back to the last migration applied at the time"
        " of command execution."
    )

    def handle(self, *args, **options):
        rollback_to: MigrationRecorder.Migration = (
            self.get_last_migration_in_current_state()
        )
        try:
            super().handle(*args, **options)
        except Exception as exc:
            self.stdout.write(" FAIL", self.style.ERROR)
            self.stdout.write("The migration has failed.", self.style.ERROR)
            self.stdout.write(str(exc), self.style.ERROR)
            self.stdout.write(self.style.MIGRATE_HEADING("Operations to perform:"))
            self.stdout.write(
                f"  Rolling back to the last migration state: {rollback_to.app} {rollback_to.name}",
                self.style.MIGRATE_LABEL,
            )
            self.stdout.write(self.style.MIGRATE_HEADING("Running rollback:"))
            last_migration: MigrationRecorder.Migration = self.get_last_migration(
                rollback_to
            )
            migration: MigrationRecorder.Migration = last_migration
            while self.has_previous(migration) and migration != rollback_to:
                self.revert_migration(migration)
                migration = migration.get_previous_by_applied()
            self.stdout.write("Exception detail:", self.style.ERROR)
            raise exc

    def get_last_migration_in_current_state(self) -> MigrationRecorder:
        return MigrationRecorder.Migration.objects.latest("id")

    def get_last_migration(self, migration: MigrationRecorder.Migration):
        while self.has_next(migration):
            migration = migration.get_next_by_applied()
        return migration

    def has_next(self, migration: MigrationRecorder.Migration) -> bool:
        try:
            migration.get_next_by_applied()
            return True
        except MigrationRecorder.Migration.DoesNotExist:
            return False

    def has_previous(self, migration: MigrationRecorder.Migration) -> bool:
        try:
            migration.get_previous_by_applied()
            return True
        except MigrationRecorder.Migration.DoesNotExist:
            return False

    def revert_migration(self, migration: MigrationRecorder.Migration):
        previous_migration: MigrationRecorder.Migration = self.get_dependency(migration)
        self.stdout.write(
            f"  Unapplying {migration.app}.{migration.name}...",
            self.style.MIGRATE_LABEL,
            ending=" ",
        )
        call_command(
            "migrate",
            previous_migration.app,
            previous_migration.name,
            no_input=True,
            verbosity=0,
        )
        self.stdout.write("OK", self.style.SUCCESS)

    def get_dependency(
        self, migration: MigrationRecorder.Migration
    ) -> MigrationRecorder.Migration:
        return MigrationRecorder.Migration.objects.filter(
            app=migration.app, id__lt=migration.id
        ).latest("id")
