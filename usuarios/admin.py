from django.contrib import admin
from .models import Usuario

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'correo', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active')
    search_fields = ('username', 'correo')

admin.site.register(Usuario, UsuarioAdmin)
