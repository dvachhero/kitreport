from django.contrib import admin
from django.urls import path
from equatingreport.views import equating_report_upload, login_view, homefd
from inventoryreport.views import inventory_report_upload, download_file, upload_success
from equatingreport.views import upload_files

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homefd, name='homefd'),
    path('equatingreportupload/', equating_report_upload, name='equating_report_upload'),
    path('login/', login_view, name='login'),
    path('homefd/', homefd, name='homefd'),
    path('inventoryreportupload/', inventory_report_upload, name='inventory_report_upload'),
    path('inventoryreportupload/success/', upload_success, name='upload_success'),
    path('inventoryreportupload/success/download-file/', download_file, name='download_file'),
    path('upload/', upload_files, name='upload_files'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
