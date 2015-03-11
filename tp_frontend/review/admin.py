from django.contrib import admin
from review.models import Entity, NoTag, Result
   

class NoTagAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'label')
    search_fields = ('frequency', 'label')
    list_filter = ('frequency',)
    ordering = (['-frequency'])

class EntityAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'entity_url', 'surface_text', 'processed', 'occupied')
    search_fields = ('frequency', 'entity_url', 'surface_text')
    list_filter = ('processed', 'occupied')
    ordering = (['-frequency'])

class ResultAdmin(admin.ModelAdmin):
    list_display = ('entity_url', 'text', 'user_defined')
    search_fields = ('entity_url', 'text')
    list_filter = ('user_defined', 'entity_url')


# Register your models here.
admin.site.register(Entity, EntityAdmin)
admin.site.register(NoTag, NoTagAdmin)
admin.site.register(Result, ResultAdmin)