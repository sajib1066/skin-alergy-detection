from django.contrib import admin
from .models import ScanHistory


@admin.register(ScanHistory)
class ScanHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'allergy_type', 'confidence', 'scan_date')
    list_filter = ('allergy_type', 'scan_date', 'user')
    search_fields = ('user__email', 'allergy_type')
    readonly_fields = ('scan_date',)
    ordering = ('-scan_date',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'scan_date')
        }),
        ('Scan Results', {
            'fields': ('allergy_type', 'confidence', 'treatment')
        }),
        ('Image', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
    ) 