from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import requests

from apps.portfolios.models import Portfolio, Project


class GitHubReposView(APIView):
    """Fetch all repos for the connected GitHub account."""
    def get(self, request):
        token = request.user.github_access_token
        if not token:
            return Response({'error': 'Connect GitHub first via Settings → GitHub.', 'connected': False}, status=400)
        resp = requests.get(
            'https://api.github.com/user/repos',
            headers={'Authorization': f'token {token}'},
            params={'sort': 'updated', 'per_page': 100, 'type': 'owner'},
            timeout=15,
        )
        if resp.status_code == 401:
            return Response({'error': 'GitHub token expired. Re-connect GitHub.', 'connected': False}, status=400)
        if resp.status_code != 200:
            return Response({'error': 'Failed to fetch repos from GitHub.'}, status=400)
        repos = []
        for r in resp.json():
            repos.append({
                'id':          r['id'],
                'name':        r['name'],
                'full_name':   r['full_name'],
                'description': r.get('description') or '',
                'html_url':    r['html_url'],
                'stars':       r['stargazers_count'],
                'forks':       r['forks_count'],
                'language':    r.get('language') or '',
                'topics':      r.get('topics', []),
                'updated_at':  r['updated_at'],
                'is_fork':     r['fork'],
                'is_private':  r['private'],
            })
        return Response({'repos': repos, 'connected': True, 'count': len(repos)})


class ImportGitHubReposView(APIView):
    """Import selected repos as portfolio projects."""
    def post(self, request, portfolio_pk):
        portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
        repos     = request.data.get('repos', [])
        if not repos:
            return Response({'error': 'No repos selected.'}, status=400)
        imported, skipped = 0, 0
        for repo in repos:
            _, created = Project.objects.get_or_create(
                portfolio=portfolio,
                github_repo_id=str(repo['id']),
                defaults={
                    'title':          repo.get('name', ''),
                    'description':    repo.get('description', ''),
                    'github_url':     repo.get('html_url', ''),
                    'stars':          repo.get('stars', 0),
                    'language':       repo.get('language', ''),
                    'tech_stack':     [repo['language']] if repo.get('language') else [],
                    'is_github_repo': True,
                }
            )
            if created:
                imported += 1
            else:
                skipped += 1
        return Response({'imported': imported, 'skipped': skipped,
                         'message': f'{imported} imported, {skipped} already exist.'})


class LinkedInProfileView(APIView):
    def get(self, request):
        token = request.user.linkedin_access_token
        if not token:
            return Response({'error': 'Connect LinkedIn first.', 'connected': False}, status=400)
        hdrs = {'Authorization': f'Bearer {token}'}
        profile = requests.get('https://api.linkedin.com/v2/me', headers=hdrs, timeout=10).json()
        try:
            ed = requests.get(
                'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
                headers=hdrs, timeout=10).json()
            email = ed['elements'][0]['handle~']['emailAddress']
        except Exception:
            email = ''
        return Response({
            'first_name': profile.get('localizedFirstName', ''),
            'last_name':  profile.get('localizedLastName', ''),
            'headline':   profile.get('headline', ''),
            'email':      email,
            'connected':  True,
        })


class LinkedInAutoFillView(APIView):
    def post(self, request):
        token = request.user.linkedin_access_token
        if not token:
            return Response({'error': 'LinkedIn not connected.'}, status=400)
        profile = requests.get('https://api.linkedin.com/v2/me',
            headers={'Authorization': f'Bearer {token}'}, timeout=10).json()
        u = request.user
        u.first_name = profile.get('localizedFirstName', u.first_name)
        u.last_name  = profile.get('localizedLastName', u.last_name)
        u.save()
        from apps.accounts.serializers import UserSerializer
        return Response(UserSerializer(u).data)
