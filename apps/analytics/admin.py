from django.contrib import admin
from .models import PortfolioView


@admin.register(PortfolioView)
class PortfolioViewAdmin(admin.ModelAdmin):
    list_display    = ('portfolio','ip_address','short_ua','viewed_at')
    list_filter     = ('viewed_at',)
    search_fields   = ('portfolio__title','ip_address')
    readonly_fields = ('portfolio','ip_address','user_agent','referrer','viewed_at')
    date_hierarchy  = 'viewed_at'

    def short_ua(self, obj):
        return obj.user_agent[:60] + '…' if len(obj.user_agent) > 60 else obj.user_agent
    short_ua.short_description = 'User Agent'
