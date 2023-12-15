from smooth_migrations.utils import SingletonMeta


class MigrationContext(metaclass=SingletonMeta):
    new_fields: list = []
    deprecated_fields: list = []
    backward_compatible_models: list = []
    deprecated_models: list = []
