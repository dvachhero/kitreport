from django.db import models

class HandbooksOsnspr(models.Model):
    id = models.BigAutoField(primary_key=True)
    pfm = models.CharField(max_length=255, verbose_name='Код завода')
    name_rp = models.CharField(max_length=255, verbose_name='Филиал')
    fio_rp = models.CharField(max_length=255, verbose_name='Ответственное лицо')
    id_rp = models.IntegerField(verbose_name='ID сотрудника')
    box = models.CharField(max_length=255, verbose_name='Основной склад')
    div = models.CharField(max_length=255, verbose_name='Дивизион')
    affiliation = models.CharField(max_length=255, verbose_name='Партнерство')

    class Meta:
        managed = False
        db_table = 'handbooks_handbooksosnspr'

class EncassationMainhandbook(models.Model):
    hb_main_acc = models.CharField(max_length=255, verbose_name='Основной счет') 
    hb_fbl3h = models.CharField(max_length=255, null=True, verbose_name='FBL3H')
    hb_code_kk = models.CharField(max_length=255, null=True, verbose_name='Код КК')
    hb_code_fn = models.CharField(max_length=255, verbose_name='Код завода')
    hb_name_rp_0660 = models.CharField(max_length=255, null=True, verbose_name='Филиал 0660')
    hb_name_rp = models.CharField(max_length=255, null=True, verbose_name='Филиал')
    hb_main_doc = models.CharField(max_length=255, verbose_name='Мандант')
