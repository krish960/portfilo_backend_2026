from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('register/',        views.RegisterView.as_view(),     name='register'),
    path('login/',           views.LoginView.as_view(),        name='login'),
    path('logout/',          views.LogoutView.as_view(),       name='logout'),
    path('token/refresh/',   TokenRefreshView.as_view(),       name='token_refresh'),
    # Profile
    path('profile/',         views.ProfileView.as_view(),      name='profile'),
    path('profile/photo/',   views.ProfilePhotoView.as_view(), name='profile_photo'),
    path('profile/password/',views.ChangePasswordView.as_view(),name='change_password'),
    # Skills
    path('skills/',          views.SkillsView.as_view(),       name='skills'),
    path('skills/<int:pk>/', views.SkillDetailView.as_view(),  name='skill_detail'),
    # Resume
    path('resume/',          views.ResumeView.as_view(),       name='resume'),
    # OAuth
    path('oauth/google/',    views.GoogleOAuthView.as_view(),  name='google_oauth'),
    path('oauth/github/',    views.GitHubOAuthView.as_view(),  name='github_oauth'),
    path('oauth/linkedin/',  views.LinkedInOAuthView.as_view(),name='linkedin_oauth'),
]
