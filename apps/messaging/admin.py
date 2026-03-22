from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('sender_name','sender_email','portfolio','subject','read_status','sent_at')
    list_filter   = ('is_read','sent_at')
    search_fields = ('sender_name','sender_email','portfolio__user__email')
    readonly_fields = ('sent_at',)
    actions       = ['mark_read','mark_unread']
    date_hierarchy = 'sent_at'

    def read_status(self, obj):
        if obj.is_read:
            return format_html('<span style="color:#94a3b8">Read</span>')
        return format_html('<span style="color:#6366f1;font-weight:700">● Unread</span>')
    read_status.short_description = 'Status'

    def mark_read(self, request, qs):
        qs.update(is_read=True)
    mark_read.short_description = 'Mark as read'

    def mark_unread(self, request, qs):
        qs.update(is_read=False)
    mark_unread.short_description = 'Mark as unread'
