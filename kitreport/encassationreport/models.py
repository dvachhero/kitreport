from django.db import models

class EncassationReportError(models.Model):
    ere_date = models.DateField(verbose_name='Дата инкассации')
    ere_comment = models.TextField(max_length=255, null=True, verbose_name='Тип ошибки')
    ere_main_acc = models.CharField(max_length=255, null=True, verbose_name='Основной счет')
    ere_code_fn = models.CharField(max_length=255, null=True, verbose_name='Код завода')
    ere_name_rp = models.CharField(max_length=255, null=True, verbose_name='Филиал')
    ere_affiliation = models.CharField(max_length=255, null=True, verbose_name='Партнерство')
    ere_saldo_in = models.FloatField(null=True, verbose_name='Вход. сальдо')
    ere_debet = models.FloatField(null=True, verbose_name='Дебет')
    ere_credit = models.FloatField(null=True, verbose_name='Кредит')
    ere_saldo_out = models.FloatField(null=True, verbose_name='Исход. сальдо')
    ere_encas_days = models.ManyToManyField('DayOfWeek')
    ere_encas_type = models.CharField(max_length=255, null=True, verbose_name='Способ инкассации')
    ere_fio_rp = models.CharField(max_length=255, null=True, verbose_name='Ответственное лицо')
    ere_id_rp = models.IntegerField(null=True, verbose_name='ID сотрудника')
    
 
class EncassationControl(models.Model):
    ec_main_city = models.CharField(max_length=255, null=True, verbose_name='Филиал') 
    encas_days = models.ManyToManyField('DayOfWeek')
    ec_encas_type = models.CharField(max_length=255, null=True, verbose_name='Способ инкассации')
    ec_code_fn = models.CharField(max_length=255, null=True, verbose_name='Код завода')
    
class HandbookFBL3H(models.Model):
    fb_fbl3h = models.CharField(max_length=255, null=True, verbose_name='FBL3H') 
    fb_code_fn = models.CharField(max_length=255, null=True, verbose_name='Код завода') 
    fb_name_rp = models.CharField(max_length=255, null=True, verbose_name='Филиал')
    fb_main_doc = models.CharField(max_length=255, null=True, verbose_name='Мандант')

class DayOfWeek(models.Model):
    DAY_CHOICES = [
        ('monday', 'пн'),
        ('tuesday', 'вт'),
        ('wednesday', 'ср'),
        ('thursday', 'чт'),
        ('friday', 'пт'),
        ('saturday', 'сб'),
        ('sunday', 'вс'),
        ('everyday', 'ежедневно'),
    ]
    day = models.CharField(max_length=9, choices=DAY_CHOICES, unique=True)
    
    def __str__(self):
        return self.get_day_display()

    

