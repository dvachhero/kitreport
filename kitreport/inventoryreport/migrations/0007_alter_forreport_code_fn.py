# Generated by Django 5.0 on 2023-12-14 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventoryreport', '0006_alter_forreport_code_fn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forreport',
            name='code_fn',
            field=models.BigIntegerField(null=True),
        ),
    ]
