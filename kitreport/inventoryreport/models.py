from django.db import models
class inventoryreportdf(models.Model):
    id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=100, blank=True)  # Позволяет пустое значение
    date_uploaded = models.DateTimeField(auto_now_add=True)  # Устанавливает текущее время при создании объекта
class inventoryreporthandbook(models.Model):
    name_rp = models.CharField(max_length=200)  # Предполагается, что это строковое поле
    comment = models.TextField(blank=True)  # Текстовое поле, может быть пустым
    fio_rp = models.CharField(max_length=200)  # Еще одно строковое поле
    id_rp = models.CharField(max_length=50, unique=True)  # Уникальный идентификатор

class inventoryreporterrors(models.Model):
    name_rp = models.CharField(max_length=200)  # Предполагается, что это строковое поле
    comment = models.TextField(blank=True)  # Текстовое поле, может быть пустым
    fio_rp = models.CharField(max_length=200)  # Еще одно строковое поле
    id_rp = models.CharField(max_length=50, unique=True)  # Уникальный идентификатор
