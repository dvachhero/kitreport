from django.contrib import admin
from django.urls import path
from equatingreport.views import equating_report_upload, login_view, homefd

urlpatterns = [
    path('admin/', admin.site.urls),
    path('equatingreportupload/', equating_report_upload, name='equating_report_upload'),
    path('login/', login_view, name='login'),
    path('homefd/', homefd, name='homefd'),

]
