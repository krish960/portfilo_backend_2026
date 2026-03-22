from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate

from apps.portfolios.models import Portfolio
from .models import PortfolioView


class DashboardAnalyticsView(APIView):
    def get(self, request):
        portfolios    = Portfolio.objects.filter(user=request.user)
        portfolio_ids = list(portfolios.values_list('id', flat=True))

        total_portfolios    = portfolios.count()
        published_portfolios = portfolios.filter(is_published=True).count()
        total_views         = PortfolioView.objects.filter(portfolio__in=portfolio_ids).count()

        now          = timezone.now()
        week_ago     = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        this_week = PortfolioView.objects.filter(
            portfolio__in=portfolio_ids, viewed_at__gte=week_ago
        ).count()
        last_week = PortfolioView.objects.filter(
            portfolio__in=portfolio_ids,
            viewed_at__gte=two_weeks_ago,
            viewed_at__lt=week_ago,
        ).count()

        growth = round(((this_week - last_week) / max(last_week, 1)) * 100, 1)

        daily_views = list(
            PortfolioView.objects
            .filter(portfolio__in=portfolio_ids, viewed_at__gte=week_ago)
            .annotate(date=TruncDate('viewed_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        # Top portfolio by views
        top_portfolio = None
        top = (
            portfolios.annotate(view_count=Count('analytics'))
                      .order_by('-view_count')
                      .first()
        )
        if top:
            top_portfolio = {
                'id':           str(top.id),
                'title':        top.title,
                'views':        top.view_count,
                'is_published': top.is_published,
                'public_url':   top.public_url,
            }

        return Response({
            'total_portfolios':    total_portfolios,
            'published_portfolios': published_portfolios,
            'total_views':         total_views,
            'this_week_views':     this_week,
            'last_week_views':     last_week,
            'weekly_growth':       growth,
            'daily_views':         daily_views,
            'top_portfolio':       top_portfolio,
        })


class PortfolioAnalyticsView(APIView):
    def get(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        now       = timezone.now()
        week_ago  = now - timedelta(days=7)

        total_views      = portfolio.analytics.count()
        unique_visitors  = portfolio.analytics.values('ip_address').distinct().count()
        this_week        = portfolio.analytics.filter(viewed_at__gte=week_ago).count()

        daily_views = list(
            portfolio.analytics
            .filter(viewed_at__gte=week_ago)
            .annotate(date=TruncDate('viewed_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        return Response({
            'total_views':     total_views,
            'unique_visitors': unique_visitors,
            'this_week_views': this_week,
            'daily_views':     daily_views,
        })
