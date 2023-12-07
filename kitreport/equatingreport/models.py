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
    name_rp = models.CharField(max_length=255)  # CharField для name_rp
    pfm = models.CharField(max_length=255)  # CharField для pfm
    street = models.CharField(max_length=255)  # CharField для street
    comment = models.TextField()  # TextField для comment, если текст может быть длинным
    fio_rp = models.CharField(max_length=255)  # CharField для fio_rp
    id_rp = models.IntegerField()  # IntegerField для id_rp, если это целое число

    def __str__(self):
        return self.name_rp  # Метод для отображения name_rp в административной панели



class EkviringData(models.Model):
    date_operation = models.CharField(max_length=100, verbose_name="Дата операции")
    terminal = models.CharField(max_length=100, verbose_name="Терминал")
    sum_operation = models.IntegerField(verbose_name="Сумма операции")

    def __str__(self):
        return f"{self.date_operation} {self.terminal} {self.sum_operation}"


class PaymentData(models.Model):
    serial_number = models.CharField(max_length=100, verbose_name="Серийный №ФН")
    date = models.CharField(max_length=100, verbose_name="Дата")
    sum = models.IntegerField(verbose_name="Сумма ВВ")
    created_by = models.CharField(max_length=100, verbose_name="Создал")
    driver = models.CharField(max_length=150, verbose_name="Водитель", blank=True, null=True)
    payment_type = models.CharField(max_length=100, verbose_name="Найм тип закр (ПЛ)")

    def __str__(self):
        return f"{self.serial_number} {self.date} {self.sum}"




#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        UserProfile.objects.create(user=instance)
#
#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.userprofile.save()