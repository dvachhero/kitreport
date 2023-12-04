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

class Eqvar(models.Model):
    terminal = models.CharField(max_length=255, blank=True, null=True)
    dateprov = models.CharField(max_length=255, blank=True, null=True)
    sumoper = models.CharField(max_length=255, blank=True, null=True)

class Eqvarkrym(models.Model):
    POS = models.CharField(max_length=255, blank=True, null=True)
    TransactionDate = models.CharField(max_length=255, blank=True, null=True)
    TransactionAmount = models.CharField(max_length=255, blank=True, null=True)

class EqvarSap(models.Model):
    SerialNumberFN = models.CharField(max_length=255, blank=True, null=True)
    Date = models.CharField(max_length=255, blank=True, null=True)
    Sum = models.CharField(max_length=255, blank=True, null=True)
    CreatedBy = models.CharField(max_length=255, blank=True, null=True)
    Driver = models.CharField(max_length=255, blank=True, null=True)
    PaymentType = models.CharField(max_length=255, blank=True, null=True)




#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        UserProfile.objects.create(user=instance)
#
#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.userprofile.save()