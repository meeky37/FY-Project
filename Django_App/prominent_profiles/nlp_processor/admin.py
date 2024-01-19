from django.contrib import admin
from .models import ProcessedFile, BoundError


def set_nlp_applied_false(modeladmin, request, queryset):
    queryset.update(nlp_applied=False)


set_nlp_applied_false.short_description = "Set NLP Applied to False for selected items"


class ProcessedFileAdmin(admin.ModelAdmin):
    list_display = ['search_term', 'file_name', 'media_path', 'nlp_applied']
    actions = [set_nlp_applied_false]


admin.site.register(ProcessedFile, ProcessedFileAdmin)
admin.site.register(BoundError)
