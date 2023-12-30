import sys
from typing import Any

from django.db.models import Field, Model

from smooth_migrations.context import MigrationContext
from smooth_migrations.exceptions import FieldDeprecatedException
from smooth_migrations.utils import is_executed_by_shell


class DeprecatedField(object):
    def __get__(self, obj: Model, *args, **kwargs) -> Any | None:
        msg = "Accessing deprecated field %s.%s" % (
            obj.__class__.__name__,
            self._get_field_name(obj),
        )
        raise FieldDeprecatedException(msg)

    def __set__(self, obj: Model, _: Any):
        msg = "Writing to deprecated field %s.%s" % (
            obj.__class__.__name__,
            self._get_field_name(obj),
        )
        raise FieldDeprecatedException(msg)

    def _get_field_name(self, obj: Model) -> str:
        for k, v in type(obj).__dict__.items():
            if v is self:
                return k
        return "<Unknown>"


def deprecated_field(instance: Field) -> Field:
    if not is_executed_by_shell():
        return DeprecatedField()
    instance.null = True
    MigrationContext.deprecated_fields.append(instance)
    return instance


def new_field(instance: Field) -> Field:
    instance.null = True
    instance.is_new_field = True
    MigrationContext.new_fields.append(instance)
    return instance
