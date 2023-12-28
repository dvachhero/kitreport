from django.contrib import admin
from .models import ForReport, sprforekv

class ForReportAdmin(admin.ModelAdmin):
    list_display = ('name_factory_rp', 'name_rp', 'name_pfm', 'number_pfm', 'code_fn', 'fio_rp', 'id_rp')
    search_fields = ['name_factory_rp']
    
class sprforekvAdmin(admin.ModelAdmin):
    list_display = ('TID', 'name_rp', 'pfm', 'street', 'comment', 'fio_rp', 'id_rp')
    search_fields = ['TID']
    
admin.site.register(ForReport, ForReportAdmin)
admin.site.register(sprforekv, sprforekvAdmin)