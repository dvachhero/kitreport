# Generated by Django 5.0 on 2023-12-11 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventoryreport', '0003_inventoryreporterrors'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_factory_rp', models.CharField(max_length=255)),
                ('name_rp', models.CharField(max_length=255)),
                ('name_pfm', models.CharField(max_length=255)),
                ('number_pfm', models.CharField(max_length=255)),
                ('code_fm', models.BigIntegerField()),
                ('fio_rp', models.CharField(max_length=255)),
                ('id_rp', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='InventoryReportError',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_rp', models.CharField(max_length=255)),
                ('comment', models.TextField()),
                ('fio_rp', models.CharField(max_length=255)),
                ('id_rp', models.IntegerField()),
            ],
        ),
        migrations.DeleteModel(
            name='inventoryreportdf',
        ),
        migrations.DeleteModel(
            name='inventoryreporterrors',
        ),
        migrations.RemoveField(
            model_name='inventoryreporthandbook',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='inventoryreporthandbook',
            name='fio_rp',
        ),
        migrations.RemoveField(
            model_name='inventoryreporthandbook',
            name='id_rp',
        ),
        migrations.RemoveField(
            model_name='inventoryreporthandbook',
            name='name_rp',
        ),
        migrations.AddField(
            model_name='inventoryreporthandbook',
            name='main_acc',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventoryreporthandbook',
            name='main_city',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventoryreporthandbook',
            name='main_doc',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]