from django.contrib import admin
from .models import HandbooksOsnspr, EncassationMainhandbook

class HandbooksOsnsprAdmin(admin.ModelAdmin):
    list_display = ['pfm', 'name_rp', 'fio_rp', 'id_rp', 'box', 'div', 'affiliation']
    search_fields = ['name_rp', 'fio_rp', 'id_rp']

class EncassationMainhandbookAdmin(admin.ModelAdmin):
    list_display = ('hb_main_acc', 'hb_fbl3h', 'hb_code_fn', 'hb_name_rp_0660', 'hb_name_rp', 'hb_main_doc')
    search_fields = ['hb_main_acc', 'hb_code_fn']

admin.site.register(EncassationMainhandbook, EncassationMainhandbookAdmin)
admin.site.register(HandbooksOsnspr, HandbooksOsnsprAdmin)
