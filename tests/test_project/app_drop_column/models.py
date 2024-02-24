from django.db import models

import smooth_migrations


class DropColumn(models.Model):
    first_field = models.IntegerField()
    second_field = smooth_migrations.deprecated_field(models.IntegerField())
