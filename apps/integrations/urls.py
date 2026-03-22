from django.urls import path
from . import views

urlpatterns = [
    path('github/repos/',                  views.GitHubReposView.as_view()),
    path('github/import/<uuid:portfolio_pk>/', views.ImportGitHubReposView.as_view()),
    path('linkedin/profile/',              views.LinkedInProfileView.as_view()),
    path('linkedin/autofill/',             views.LinkedInAutoFillView.as_view()),
]
