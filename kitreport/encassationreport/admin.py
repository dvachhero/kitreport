from django.contrib import admin
from .models import EncassationControl, DayOfWeek, EncassationReportError, HandbookFBL3H

class DayOfWeekAdmin(admin.ModelAdmin):
    list_display = ('day', 'get_day_display')
    ordering = ('day',)

class EncassationControlAdmin(admin.ModelAdmin):
    list_display = ('ec_main_city', 'display_encas_days', 'ec_encas_type', 'ec_code_fn')
    search_fields = ['ec_main_city', 'display_encas_days', 'ec_encas_type', 'ec_code_fn']
    filter_horizontal = ('encas_days',)
    
    def display_encas_days(self, obj):
        return ", ".join([day.get_day_display() for day in obj.encas_days.all()])
    display_encas_days.short_description = 'Установленные дни'

class HandbookFBL3HAdmin(admin.ModelAdmin):
    list_display = ('fb_fbl3h', 'fb_code_fn', 'fb_name_rp', 'fb_main_doc')
    search_fields = ['fb_fbl3h', 'fb_code_fn', 'fb_name_rp', 'fb_main_doc']

class EncassationReportErrorAdmin(admin.ModelAdmin):
    list_display = (
        'ere_date', 'ere_comment', 'ere_main_acc', 
        'ere_code_fn', 'ere_name_rp', 'ere_affiliation',
        'ere_saldo_in', 'ere_debet', 'ere_credit', 
        'ere_saldo_out', 'display_ere_encas_days', 'ere_encas_type',
        'ere_fio_rp', 'ere_id_rp'
        )
    search_fields = [
        'ere_main_acc', 'ere_code_fn', 'ere_name_rp',
        'ere_affiliation', 'ere_saldo_in', 'ere_debet',
        'ere_credit', 'ere_saldo_out', 'ere_encas_type',
        'ere_fio_rp', 'ere_id_rp']
    
    def display_ere_encas_days(self, obj):
        return ", ".join([day.get_day_display() for day in obj.encas_days.all()])
    display_ere_encas_days.short_description = 'Установленные дни'

admin.site.register(DayOfWeek, DayOfWeekAdmin)
admin.site.register(HandbookFBL3H, HandbookFBL3HAdmin)
admin.site.register(EncassationControl, EncassationControlAdmin)
admin.site.register(EncassationReportError, EncassationReportErrorAdmin)

