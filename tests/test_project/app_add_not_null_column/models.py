from django.db import models

import smooth_migrations


@smooth_migrations.backward_compatible_model
class AddNotNullColumn(models.Model):
    first_field = models.IntegerField()
    new_not_null_field = smooth_migrations.new_field(models.IntegerField())
