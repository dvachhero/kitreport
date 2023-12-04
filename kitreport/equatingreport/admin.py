from django.contrib import admin
from .models import UserProfile, InventoryReport500Handbook, InventoryReport500

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'department']
    search_fields = ['user__username','full_name', 'department']

admin.site.register(UserProfile, UserProfileAdmin)

class InventoryReport500HandbookAdmin(admin.ModelAdmin):
    list_display = ('BE', 'Financial', 'DocumentNumber', 'DateProcessed', 'Processed')

class InventoryReport500Admin(admin.ModelAdmin):
    list_display = ('BE', 'Financial', 'DocumentNumber', 'DateProcessed', 'Processed')

admin.site.register(InventoryReport500Handbook, InventoryReport500HandbookAdmin)
admin.site.register(InventoryReport500, InventoryReport500Admin)

