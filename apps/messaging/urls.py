from django.urls import path
from . import views

urlpatterns = [
    path('send/<str:slug>/', views.SendMessageView.as_view()),
    path('inbox/',               views.InboxView.as_view()),
    path('<int:pk>/',            views.MessageDetailView.as_view()),
]
