from django.contrib import admin
from django.urls import path
from equatingreport.views import equating_report_upload, login_view, homefd
from inventoryreport.views import inventory_report_upload
from equatingreport.views import upload_files, check_fn



urlpatterns = [
    path('admin/', admin.site.urls),
    path('equatingreportupload/', upload_files, name='equating_report_upload'),
    path('login/', login_view, name='login'),
    path('homefd/', homefd, name='homefd'),
    path('inventoryreportupload/', inventory_report_upload, name='inventory_report_upload'),
    path('check_fn/', check_fn, name='check_fn'),
]
