# Django Smooth Migrations

Is a Django library that helps you make changes to your models in a way that is compatible with previous versions of your codebase. It also provides a migration command that automatically rolls back any failed migrations. This makes it easier to deploy new versions of your application without disrupting existing users.. It can help you to make deployments smoother (Blue/Green Deployments), increase compatibility, and reduce errors.

Django Smooth Migrations uses a two-step process to make model changes compatible with previous versions. It is designed to allow migrations in the current version to make database changes that enable compatibility, leaving validation to be done at the application level. These validations are then applied to the database in a new migration in the next version.

## Quick installation

```
pip install django-smooth-migrations
```

And add to your ``INSTALLED_APPS``:

```python
INSTALLED_APPS = [
    ...,
    "smooth_migrations",
    ...,
]
```

## Apply migrations safely

The command `apply_migrations` attempts to run the migrations normally, as the `migrate` command would. If any of the migrations fail, a rollback is performed in the same order in which they were applied, until the state of the database is the same as it was at the time the command was executed.

```bash
> python manage.py apply_migrations

Operations to perform:
  Apply all migrations: admin, auth, common, contenttypes, demo, sessions
Running migrations:
  Applying demo.0002_alter_mymodel_field1... OK
  Applying demo.0003_alter_field2... OK
  Applying demo.0004_alter_field3... OK
  Applying demo.0005_remove_field2... OK
  Applying demo.0006_custom_fail_migration... FAIL
The migration has failed.
column "field3" of relation "demo_mymodel" already exists
Operations to perform:
  Rolling back to the last migration state: demo 0001_initial
Running rollback:
  Unapplying dashboards.0005_remove_field2... OK
  Unapplying dashboards.0004_alter_field3 copy... OK
  Unapplying dashboards.0003_alter_field2... OK
  Unapplying dashboards.0002_alter_mymodel_field1... OK
Exception detail:
Traceback (most recent call last):
  File "/opt/pysetup/.venv/lib/python3.10/site-packages/django/db/backends/utils.py", line 89, in _execute
    return self.cursor.execute(sql, params)
psycopg2.errors.DuplicateColumn: column "field3" of relation "demo_mymodel" already exists
```