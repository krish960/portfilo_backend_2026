from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include

def home(request):
    return HttpResponse("🚀 Portfolio Backend Running")

urlpatterns = [
    path('', home),  # 👈 ADD THIS
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/portfolios/', include('apps.portfolios.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/messages/', include('apps.messaging.urls')),
    path('api/v1/integrations/', include('apps.integrations.urls')),
]