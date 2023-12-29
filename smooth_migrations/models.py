from typing import Callable

from django.db.models import Manager, Model

from smooth_migrations.context import MigrationContext
from smooth_migrations.exceptions import ModelDeprecatedException, NotNullableFieldException
from smooth_migrations.utils import is_executed_by_shell


class DeprecatedModelManager(Manager):
    def get_queryset(self):
        raise ModelDeprecatedException()


def deprecated_model(instance: Model) -> Model:
    if not is_executed_by_shell():
        instance.objects = DeprecatedModelManager()
    MigrationContext.deprecated_models.append(instance)
    return instance


def backward_compatible_model(instance: Model) -> Model:
    if not is_executed_by_shell():
        super_save: Callable = instance.save

        def save(instance: Model, *args, **kwargs) -> None:
            for field in instance._meta.get_fields():
                is_new_field: bool = getattr(field, "is_new_field", False)
                if is_new_field and getattr(instance, field.name) is None:
                    raise NotNullableFieldException(
                        f"{instance.__class__.__name__}.{field.name}"
                    )
            super_save(instance, *args, **kwargs)

        instance.save = save
    MigrationContext.deprecated_models.append(instance)
    return instance
