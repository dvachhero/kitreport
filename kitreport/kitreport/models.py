from django.db import models

class ForReport(models.Model):
    name_factory_rp = models.CharField(max_length=255)
    name_rp = models.CharField(max_length=255)
    name_pfm = models.CharField(max_length=255, null=True)
    number_pfm = models.CharField(max_length=255, null=True)
    code_fn = models.BigIntegerField(null=True)
    fio_rp = models.CharField(max_length=255, null=True)
    id_rp = models.IntegerField(null=True)
    
class sprforekv(models.Model):
    TID = models.CharField(max_length=255)
    name_rp = models.TextField()
    pfm = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    comment = models.TextField()
    fio_rp = models.CharField(max_length=255)
    id_rp = models.IntegerField()
