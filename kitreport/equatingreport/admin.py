from django.contrib import admin
from .models import UserProfile, sprforekv, sprforfn

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name', 'department']
    search_fields = ['user__username','full_name', 'department']

admin.site.register(UserProfile, UserProfileAdmin)


class SprForEkvAdmin(admin.ModelAdmin):
    # Эти поля будут отображаться в списке
    list_display = ('TID', 'name_rp', 'pfm', 'street', 'fio_rp', 'id_rp')

    # Эти поля будут использоваться для фильтрации в списке
    list_filter = ('pfm', 'street', 'fio_rp')

    # Поля, по которым будет осуществляться поиск
    search_fields = ('name_rp', 'street', 'comment', 'fio_rp')
admin.site.register(sprforekv, SprForEkvAdmin)

class SprForFnAdmin(admin.ModelAdmin):
    # Эти поля будут отображаться в списке
    list_display = ('code_fn', 'name_rp', 'pfm')

    # Поля, по которым будет осуществляться поиск
    search_fields = ('code_fn', 'name_rp', 'pfm')
admin.site.register(sprforfn, SprForFnAdmin)


