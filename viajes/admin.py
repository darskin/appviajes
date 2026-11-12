from django.contrib import admin

from .models import Choice, Destino, Voto


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'presupuesto', 'propietario')
    list_filter = ('propietario',)
    search_fields = ('nombre', 'descripcion')
    inlines = [ChoiceInline]


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'destino', 'opcion')
    list_filter = ('destino',)


admin.site.register(Choice)
