# Generated by Django 4.2.7 on 2023-12-04 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventoryreport', '0002_rename_yourmodelname_inventoryreportdf_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='inventoryreporterrors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_rp', models.CharField(max_length=200)),
                ('comment', models.TextField(blank=True)),
                ('fio_rp', models.CharField(max_length=200)),
                ('id_rp', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
