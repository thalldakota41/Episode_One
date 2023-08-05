from django.contrib import admin
from .models import Creator, Tag, Show, Comment, StaffFavorite, CreatorOfTheMonth, InfluentialShow
from dal import autocomplete


@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = []


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['genre']
    autocomplete_fields = ['shows']


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    search_fields = ['title']
    autocomplete_fields = ['tags', 'favorites','creators']


@admin.register(StaffFavorite)
class StaffFavoriteAdmin(admin.ModelAdmin):
    search_fields = ['show__title']
    autocomplete_fields = ['show']


@admin.register(InfluentialShow)
class InfluentialShowAdmin(admin.ModelAdmin):
    search_fields = []
    autocomplete_fields = ['show']

@admin.register(CreatorOfTheMonth)
class CreatorOfTheMonthAdmin(admin.ModelAdmin):
    search_fields = []
    autocomplete_fields = ['creator']

admin.site.register(Comment)

