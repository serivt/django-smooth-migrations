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
  Unapplying demo.0005_remove_field2... OK
  Unapplying demo.0004_alter_field3 copy... OK
  Unapplying demo.0003_alter_field2... OK
  Unapplying demo.0002_alter_mymodel_field1... OK
Exception detail:
Traceback (most recent call last):
  File "/opt/pysetup/.venv/lib/python3.10/site-packages/django/db/backends/utils.py", line 89, in _execute
    return self.cursor.execute(sql, params)
psycopg2.errors.DuplicateColumn: column "field3" of relation "demo_mymodel" already exists
```
Once the version is released and the migrations are applied to the production environment, you can remove the wrapper method (`new_field`) and generate new migrations (`makemigrations`). This will move the validations from the application level to the database level in the next version.

## Backward incompatibilities

:rotating_light: **Added required (NOT NULL) columns**

Adding a new column that cannot be null will cause incompatibility with the previous version of the codebase, as attempting to insert a row into the table will result in the error `column cannot be null`.

A common mistake is to think that simply specifying a default value in a Django model field will prevent errors. This is because Django uses the default value to fill a new column in existing rows and to set an unspecified column value to its default value. The latter is done by Django at the application level, not by the database, because the default value was removed during the migration. You can read more about this in the [Django and its default values blog post](https://medium.com/botify-labs/django-and-its-default-values-c21a13cff9f).

:white_check_mark: **Solution**

In order to add `field3`, it must be wrapped with the `new_field()` method, which will mark it as nullable internally to make it compatible with the previous codebase. However, we want to ensure that in the new codebase, this field is not optional. To do this, we decorate the model with `backward_compatible_model`, which will make the field non-nullable at the application level.

```python
from django.db import models

from smooth_migrations.fields import new_field
from smooth_migrations.models import backward_compatible_model


@backward_compatible_model
class MyModel(models.Model):
    field1 = models.CharField(max_lenght=100)
    field2 = models.IntegerField()
    field3 = new_field(models.IntegerField())
```

***

:rotating_light: **Dropping columns**

Delete operations often cause errors during deployment because Django makes all column names explicit when searching for a model object in the database. This can cause `Column does not exists` errors in the previous codebase. 

:white_check_mark: **Solution**

```python
from django.db import models

from smooth_migrations.fields import deprecated_field


class MyModel(models.Model):
    field1 = deprecated_field(models.CharField(max_lenght=100))
    field2 = models.IntegerField()
    field3 = models.IntegerField()
```

So if you try to access it you will get an exception, but the column will still exist in the database.

```python
MyModel.objects.last().field_1

File ~/smooth_migrations/fields.py:24, in DeprecatedField.__get__(self, obj, type)
     19 msg = "Accessing deprecated field %s.%s" % (
     20     obj.__class__.__name__,
     21     self._get_field_name(obj),
     22 )
     23 raise FieldDeprecatedException(msg)

FieldDeprecatedException: Accessing deprecated field MyModel.field1
```

***

:rotating_light: **Dropping tables**

With the previous codebase, it is possible that an attempt will be made to query a deleted table to retrieve rows. However, this will fail.

:white_check_mark: **Solution**

```python
from django.db import models

from smooth_migrations.models import deprecate_model


@deprecate_model
class MyModel(models.Model):
    field1 = models.CharField(max_lenght=100)
    field2 = models.IntegerField()
    field3 = models.IntegerField()
```
So if you try to query data it you will get an exception, but the table will still exist in the database.

```python
File /opt/pysetup/.venv/lib/python3.10/site-packages/django/db/models/manager.py:85, in BaseManager._get_queryset_methods.<locals>.create_method.<locals>.manager_method(self, *args, **kwargs)
     84 def manager_method(self, *args, **kwargs):
---> 85     return getattr(self.get_queryset(), name)(*args, **kwargs)

File ~/smooth_migrations/models.py:11, in DeprecatedModelManager.get_queryset(self)
     10 def get_queryset(self):
---> 11     raise ModelDeprecatedException()

ModelDeprecatedException: This model is no longer supported because it is deprecated and will be removed in the next version.
```

### Backward incompatibilities pending to be resolved

* Renaming columns
* Renaming tables
* Altering columns (which can be backward compatible and potentially ignored)
* Adding a unique constraint

## Show migration changes

Once a new version is released, it is common to want the changes that were made in the previous version to be applied permanently in the next version. This includes moving application-level validations to database-level. To do this, you can use the show_migration_changes command to list all the changes that were made to models that are backward compatible. Then, you can remove this backward compatibility and generate new migrations to apply the changes permanently.

```
python manage.py show_migration_changes
New fields:
  demo.MyModel.field3
Deprecated fields:
  demo.MyModel.field1
Deprecated models:
  <class 'demo.models.MyDeprecatedModel'>
```