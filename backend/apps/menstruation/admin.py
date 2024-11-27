from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from apps.menstruation.models import Symptom

class SymptomAdmin(admin.ModelAdmin):
    list_display = ('id_symptom','title', 'symptom_type', 'description')
    list_filter = ('symptom_type', )
    search_fields = ('title', 'description')
    ordering = ('-id_symptom',)
    actions = ['modifier_le_symptom']

    def modifier_le_symptom(self, request, queryset):
        symptom = queryset.first()
        if symptom:
            url = reverse('admin:menstruation_symptom_change', args=[symptom.id_symptom])
            return HttpResponseRedirect(url)
    
admin.site.register(Symptom, SymptomAdmin)