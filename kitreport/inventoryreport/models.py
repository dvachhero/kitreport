from django.db import models

class InventoryReportHandbook(models.Model):
    main_acc = models.CharField(max_length=255)
    main_city = models.CharField(max_length=255)
    main_doc = models.CharField(max_length=255)

class InventoryReportError(models.Model):
    name_rp = models.CharField(max_length=255)
    comment = models.TextField()  # TextField для хранения longtext
    fio_rp = models.CharField(max_length=255, null=True)
    id_rp = models.IntegerField(null=True)

class ForReport(models.Model):
    name_factory_rp = models.CharField(max_length=255)
    name_rp = models.CharField(max_length=255)
    name_pfm = models.CharField(max_length=255, null=True)
    number_pfm = models.CharField(max_length=255, null=True)
    code_fn = models.BigIntegerField(null=True)
    fio_rp = models.CharField(max_length=255, null=True)
    id_rp = models.IntegerField(null=True)