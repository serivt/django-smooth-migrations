import sys
from threading import Lock


def is_executed_by_shell() -> bool:
    return bool(
        set(sys.argv)
        & {
            "makemigrations",
            "migrate",
            "apply_migrations",
            "showmigrations",
            "show_migration_changes",
        }
    )


class SingletonMeta(type):
    """This is a thread-safe implementation of the Singleton pattern.

    Have a lock object that will be used to synchronize threads during first
    access to the Singleton.

    How to implement it:

    class Singleton(metaclass=SingletonMeta):
        value: str = None

        def __init__(self, value: str) -> None:
            self.value = value

    """

    _instances: dict["SingletonMeta", "SingletonMeta"] = {}
    _lock: Lock = Lock()

    def __call__(cls: "SingletonMeta", *args, **kwargs) -> "SingletonMeta":
        """A thread-safe implementation that prevents potential changes in the
        `__init__` method from affecting the returned instance, ensuring that
        only a single instance of the class exists throughout the execution
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
