from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from .models import InventoryReportHandbook, InventoryReportError, ForReport
import codecs

# Класс CSV формата с UTF-16 кодировкой
class UTF16CSV(base_formats.CSV):
    def get_title(self):
        return "CSV (UTF-16 LE with BOM)"

    def create_dataset(self, in_stream, **kwargs):
        # Чтение файла с учетом BOM
        if not in_stream.startswith(codecs.BOM_UTF16_LE):
            in_stream = codecs.BOM_UTF16_LE + in_stream
        return super().create_dataset(in_stream.decode('utf-16-le'), **kwargs)

    def export_data(self, dataset, **kwargs):
    
        return codecs.BOM_UTF16_LE + dataset.csv.encode('utf-16-le')

# Ресурсы для каждой модели
class InventoryReportHandbookResource(resources.ModelResource):
    class Meta:
        model = InventoryReportHandbook
        import_id_fields = ('id',)
        export_order = ('main_acc', 'main_city', 'main_doc')
        skip_unchanged = True
        report_skipped = False

class InventoryReportErrorResource(resources.ModelResource):
    class Meta:
        model = InventoryReportError
        import_id_fields = ('id',)
        export_order = ('name_rp', 'comment', 'fio_rp', 'id_rp')
        skip_unchanged = True
        report_skipped = False

class ForReportResource(resources.ModelResource):
    class Meta:
        model = ForReport
        import_id_fields = ('id',)
        export_order = ('name_factory_rp', 'name_rp', 'name_pfm', 'number_pfm', 'code_fn', 'fio_rp', 'id_rp')
        skip_unchanged = True
        report_skipped = False

# Админ-классы для моделей
class InventoryReportHandbookAdmin(ImportExportModelAdmin):
    resource_class = InventoryReportHandbookResource
    list_display = ('main_acc', 'main_city', 'main_doc')
    formats = [UTF16CSV]

class InventoryReportErrorAdmin(ImportExportModelAdmin):
    resource_class = InventoryReportErrorResource
    list_display = ('name_rp', 'comment', 'fio_rp', 'id_rp')
    formats = [UTF16CSV]

class ForReportAdmin(ImportExportModelAdmin):
    resource_class = ForReportResource
    list_display = ('name_factory_rp', 'name_rp', 'name_pfm', 'number_pfm', 'code_fn', 'fio_rp', 'id_rp')
    formats = [UTF16CSV]

# Регистрация в админке
admin.site.register(InventoryReportHandbook, InventoryReportHandbookAdmin)
admin.site.register(InventoryReportError, InventoryReportErrorAdmin)
admin.site.register(ForReport, ForReportAdmin)
