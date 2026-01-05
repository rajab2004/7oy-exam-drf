from django.contrib import admin
from .models import TimeSlot, Appointment


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_available', 'created_at')
    list_filter = ('doctor', 'date', 'is_available')
    search_fields = ('doctor__username', 'doctor__email')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('doctor', 'date', 'start_time', 'end_time', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'timeslot', 'status', 'created_at')
    list_filter = ('status', 'doctor', 'created_at')
    search_fields = ('doctor__username', 'patient__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('doctor', 'patient', 'timeslot')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('doctor', 'patient', 'timeslot', 'status')
        }),
        ('Medical Information', {
            'fields': ('notes', 'symptoms'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_confirmed', 'mark_cancelled', 'mark_completed']
    
    def mark_confirmed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f"{updated} appointments confirmed.")
    mark_confirmed.short_description = "Mark selected appointments as confirmed"
    
    def mark_cancelled(self, request, queryset):
        for appointment in queryset:
            appointment.status = 'cancelled'
            appointment.save()
        self.message_user(request, f"{queryset.count()} appointments cancelled.")
    mark_cancelled.short_description = "Mark selected appointments as cancelled"
    
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f"{updated} appointments marked as completed.")
    mark_completed.short_description = "Mark selected appointments as completed"