# Generated by Django 4.2.10 on 2024-02-24 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_add_not_null_column', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='addnotnullcolumn',
            name='new_not_null_field',
            field=models.IntegerField(null=True),
        ),
    ]
