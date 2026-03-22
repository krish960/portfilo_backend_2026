from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ── Admin branding ────────────────────────────────────────────────────────────
admin.site.site_header  = '🗂  PortfolioAI Admin'
admin.site.site_title   = 'PortfolioAI'
admin.site.index_title  = 'Control Panel'

urlpatterns = [
    path('admin/',               admin.site.urls),
    path('api/v1/auth/',         include('apps.accounts.urls')),
    path('api/v1/portfolios/',   include('apps.portfolios.urls')),
    path('api/v1/analytics/',    include('apps.analytics.urls')),
    path('api/v1/messages/',     include('apps.messaging.urls')),
    path('api/v1/integrations/', include('apps.integrations.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
