from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',          views.DashboardAnalyticsView.as_view()),
    path('portfolio/<uuid:pk>/',views.PortfolioAnalyticsView.as_view()),
]
