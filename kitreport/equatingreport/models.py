from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, default='Default Department')
    full_name = models.CharField(max_length=255, default='Default FIO')
    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return self.user.username

class sprforekv(models.Model):
    TID = models.CharField(max_length=255)  # Автоинкрементируемое поле для идентификатора
    name_rp = models.TextField()  # CharField для name_rp
    pfm = models.CharField(max_length=255)  # CharField для pfm
    street = models.CharField(max_length=255)  # CharField для street
    comment = models.TextField()  # TextField для comment, если текст может быть длинным
    fio_rp = models.CharField(max_length=255)  # CharField для fio_rp
    id_rp = models.IntegerField()  # IntegerField для id_rp, если это целое число

    def __str__(self):
        return self.name_rp  # Метод для отображения name_rp в административной панели

class sprforfn(models.Model):
    code_fn = models.TextField(verbose_name="code_fn")
    name_rp = models.TextField(verbose_name="name_rp")
    pfm = models.TextField(verbose_name="pfm")

    def __str__(self):
        return self.code_fn


class EkviringData(models.Model):
    date_operation = models.CharField(max_length=100, verbose_name="Дата операции")
    terminal = models.CharField(max_length=100, verbose_name="Терминал")
    sum_operation = models.IntegerField(verbose_name="Сумма операции")

    def __str__(self):
        return f"{self.date_operation} {self.terminal} {self.sum_operation}"

class EkviringData_enriched(models.Model):
    date_operation = models.DateField(verbose_name="ДАТАОПЕРАЦИИ")
    terminal = models.BigIntegerField(verbose_name="ТЕРМИНАЛ")
    sum_operation = models.IntegerField(verbose_name="СУММАОПЕРАЦИИ")
    TID = models.CharField(max_length=255, verbose_name="TID")
    name_rp = models.TextField(verbose_name="name_rp")
    pfm = models.TextField(verbose_name="pfm")
    fio_rp = models.TextField(verbose_name="fio_rp")
    id_rp = models.TextField(verbose_name="id_rp")
    id_x = models.TextField(verbose_name="id_x")
    id_y = models.TextField(verbose_name="id_y")
    street = models.TextField(verbose_name="street")
    comment = models.TextField(verbose_name="comment")
    def __str__(self):
        return self.TID


class PaymentData(models.Model):
    code_fn = models.CharField(max_length=100, verbose_name="Серийный №ФН")
    date = models.CharField(max_length=100, verbose_name="Дата")
    sum = models.IntegerField(verbose_name="Сумма ВВ")
    created_by = models.CharField(max_length=100, verbose_name="Создал")
    driver = models.CharField(max_length=150, verbose_name="Водитель", blank=True, null=True)
    payment_type = models.CharField(max_length=100, verbose_name="Найм тип закр (ПЛ)")

    def __str__(self):
        return f"{self.serial_number} {self.date} {self.sum}"

class PaymentData_enriched(models.Model):
    code_fn = models.TextField(verbose_name="СЕРИЙНЫЙ№ФН")
    date = models.DateField(verbose_name="ДАТА")
    sum = models.IntegerField(verbose_name="СУММАВВ")
    created_by = models.TextField(verbose_name="СОЗДАЛ")
    driver = models.TextField(verbose_name="ВОДИТЕЛЬ")
    payment_type = models.TextField(verbose_name="НАИМТИПЗАКР(ПЛ)")
    code_fn = models.TextField(verbose_name="code_fn")
    pfm = models.TextField(verbose_name="pfm")
    id_x = models.TextField(verbose_name="id_x")
    id_y = models.TextField(verbose_name="id_y")
    name_rp = models.TextField(verbose_name="name_rp")
    def __str__(self):
        return self.serial_number_fn





#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        UserProfile.objects.create(user=instance)
#
#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.userprofile.save()