from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'department']
    search_fields = ['user__username','full_name', 'department']

admin.site.register(UserProfile, UserProfileAdmin)

