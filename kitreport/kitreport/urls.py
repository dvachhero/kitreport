from django.contrib import admin
from django.urls import path
from equatingreport.views import equating_report_upload, login_view, homefd
from inventoryreport.views import inventory_report_upload, inventory_download_file, inventory_upload_success
from encassationreport.views import encassation_report_upload, encassation_download_file, encassation_upload_success
from equatingreport.views import upload_files, check_fn

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homefd, name='homefd'),
    path('equatingreportupload/', upload_files, name='equating_report_upload'),
    path('login/', login_view, name='login'),
    path('homefd/', homefd, name='homefd'),
    path('inventoryreportupload/', inventory_report_upload, name='inventory_report_upload'),
    path('inventoryreportupload/download/', inventory_upload_success, name='inventory_upload_success'),
    path('inventoryreportupload/download/download-file/', inventory_download_file, name='inventory_download_file'),
    path('encassationreportupload/', encassation_report_upload, name='encassation_report_upload'),
    path('encassationreportupload/download/', encassation_upload_success, name='encassation_upload_success'),
    path('encassationreportupload/download/download-file/', encassation_download_file, name='encassation_download_file'),
    path('check_fn/', check_fn, name='check_fn'),
  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT_IYR) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT_ISR)
