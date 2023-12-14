import sys

def is_executed_by_shell():
    return set(sys.argv) & {"makemigrations", "migrate", "apply_migrations", "showmigrations"}