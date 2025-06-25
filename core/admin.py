from django.contrib import admin
from .models import Artist, Album, ArtistaSolo, GrupoMusical
from django.contrib.auth.models import Group


admin.site.site_header = "Painel de admin"

admin.site.site_title = "Admin"

admin.site.index_title = "Bem vindo ao painel de controlo!"

@admin.register(ArtistaSolo)
class ArtistaSoloAdmin(admin.ModelAdmin):
    exclude = ('favorito',)

@admin.register(GrupoMusical)
class GrupoMusicalAdmin(admin.ModelAdmin):
    exclude = ('favorito',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    exclude = ('favorito',)

admin.site.unregister(Group)
