from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Portfolio, PortfolioSection, Project, Experience, Education
from .serializers import (
    PortfolioSerializer, PortfolioListSerializer, CreatePortfolioSerializer,
    PortfolioSectionSerializer, ProjectSerializer,
    ExperienceSerializer, EducationSerializer,
)
from apps.analytics.models import PortfolioView


class PortfolioListCreateView(APIView):
    def get(self, request):
        portfolios = Portfolio.objects.filter(user=request.user)
        return Response(PortfolioListSerializer(portfolios, many=True).data)

    def post(self, request):
        serializer = CreatePortfolioSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            portfolio = serializer.save()
            return Response(PortfolioSerializer(portfolio).data, status=201)
        return Response(serializer.errors, status=400)


class PortfolioDetailView(APIView):
    def get_object(self, pk, user):
        return get_object_or_404(Portfolio, pk=pk, user=user)

    def get(self, request, pk):
        return Response(PortfolioSerializer(self.get_object(pk, request.user)).data)

    def patch(self, request, pk):
        portfolio  = self.get_object(pk, request.user)
        serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        self.get_object(pk, request.user).delete()
        return Response(status=204)


class PublishPortfolioView(APIView):
    def post(self, request, pk):
        portfolio            = get_object_or_404(Portfolio, pk=pk, user=request.user)
        portfolio.is_published = not portfolio.is_published
        portfolio.save()
        return Response({
            'is_published': portfolio.is_published,
            'message':      'Published' if portfolio.is_published else 'Unpublished',
        })


# ── Public portfolio (no auth required, tracks views) ────────────────────────

class PublicPortfolioView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        portfolio = get_object_or_404(Portfolio, slug=slug, is_published=True)
        # Track view
        PortfolioView.objects.create(
            portfolio   = portfolio,
            ip_address  = request.META.get('REMOTE_ADDR', ''),
            user_agent  = request.META.get('HTTP_USER_AGENT', '')[:500],
            referrer    = request.META.get('HTTP_REFERER', '')[:200],
        )
        return Response(PortfolioSerializer(portfolio).data)


# ── Sections ──────────────────────────────────────────────────────────────────

class SectionUpdateView(APIView):
    def patch(self, request, portfolio_pk, pk):
        section    = get_object_or_404(
            PortfolioSection, pk=pk,
            portfolio__pk=portfolio_pk, portfolio__user=request.user,
        )
        serializer = PortfolioSectionSerializer(section, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ReorderSectionsView(APIView):
    def post(self, request, portfolio_pk):
        portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
        for item in request.data.get('sections', []):
            PortfolioSection.objects.filter(
                pk=item['id'], portfolio=portfolio
            ).update(order=item['order'])
        return Response({'message': 'Sections reordered.'})


# ── Projects ──────────────────────────────────────────────────────────────────

class ProjectListCreateView(APIView):
    def get(self, request, portfolio_pk):
        portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
        return Response(ProjectSerializer(portfolio.projects.all(), many=True).data)

    def post(self, request, portfolio_pk):
        portfolio  = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(portfolio=portfolio)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ProjectDetailView(APIView):
    def get_object(self, pk, portfolio_pk, user):
        return get_object_or_404(
            Project, pk=pk, portfolio__pk=portfolio_pk, portfolio__user=user
        )

    def patch(self, request, portfolio_pk, pk):
        project    = self.get_object(pk, portfolio_pk, request.user)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, portfolio_pk, pk):
        self.get_object(pk, portfolio_pk, request.user).delete()
        return Response(status=204)


# ── Experience ────────────────────────────────────────────────────────────────

class ExperienceListCreateView(APIView):
    def get(self, request, portfolio_pk):
        portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
        return Response(ExperienceSerializer(portfolio.experiences.all(), many=True).data)

    def post(self, request, portfolio_pk):
        portfolio  = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
        serializer = ExperienceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(portfolio=portfolio)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ExperienceDetailView(APIView):
    def patch(self, request, portfolio_pk, pk):
        exp        = get_object_or_404(
            Experience, pk=pk, portfolio__pk=portfolio_pk, portfolio__user=request.user
        )
        serializer = ExperienceSerializer(exp, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, portfolio_pk, pk):
        get_object_or_404(
            Experience, pk=pk, portfolio__pk=portfolio_pk, portfolio__user=request.user
        ).delete()
        return Response(status=204)


# ── Education ─────────────────────────────────────────────────────────────────

class EducationListCreateView(APIView):
    def get(self, request, portfolio_pk):
        portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
        return Response(EducationSerializer(portfolio.educations.all(), many=True).data)

    def post(self, request, portfolio_pk):
        portfolio  = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
        serializer = EducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(portfolio=portfolio)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, portfolio_pk, pk):
        get_object_or_404(
            Education, pk=pk, portfolio__pk=portfolio_pk, portfolio__user=request.user
        ).delete()
        return Response(status=204)
