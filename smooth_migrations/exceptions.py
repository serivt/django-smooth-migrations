class ModelDeprecatedException(Exception):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            f"This model is no longer supported because it is deprecated and will be removed in the next version."
        )


class FieldDeprecatedException(Exception):
    ...


class NotNullableFieldException(Exception):
    def __init__(self, field_name: str) -> None:
        super().__init__(f"The field '{field_name}' cannot be null.")
