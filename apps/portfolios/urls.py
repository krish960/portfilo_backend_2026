from django.urls import path
from . import views

urlpatterns = [
    path('',                                          views.PortfolioListCreateView.as_view()),
    path('<uuid:pk>/',                                views.PortfolioDetailView.as_view()),
    path('<uuid:pk>/publish/',                        views.PublishPortfolioView.as_view()),
    # Sections
    path('<uuid:portfolio_pk>/sections/<int:pk>/',    views.SectionUpdateView.as_view()),
    path('<uuid:portfolio_pk>/sections/reorder/',     views.ReorderSectionsView.as_view()),
    # Projects
    path('<uuid:portfolio_pk>/projects/',             views.ProjectListCreateView.as_view()),
    path('<uuid:portfolio_pk>/projects/<int:pk>/',    views.ProjectDetailView.as_view()),
    # Experience
    path('<uuid:portfolio_pk>/experience/',           views.ExperienceListCreateView.as_view()),
    path('<uuid:portfolio_pk>/experience/<int:pk>/',  views.ExperienceDetailView.as_view()),
    # Education
    path('<uuid:portfolio_pk>/education/',            views.EducationListCreateView.as_view()),
    path('<uuid:portfolio_pk>/education/<int:pk>/',   views.EducationListCreateView.as_view()),
    # Public (no auth)
    path('public/<str:slug>/',                    views.PublicPortfolioView.as_view()),
]
