from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
import requests

from .models import UserSkill, Resume
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    UpdateProfileSerializer, UserSkillSerializer,
    ChangePasswordSerializer, ResumeSerializer,
)

User = get_user_model()


def make_tokens(user):
    r = RefreshToken.for_user(user)
    return {'refresh': str(r), 'access': str(r.access_token)}


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            user = s.save()
            return Response({'user': UserSerializer(user).data, 'tokens': make_tokens(user)}, status=201)
        return Response(s.errors, status=400)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        s = LoginSerializer(data=request.data)
        if s.is_valid():
            user = s.validated_data['user']
            return Response({'user': UserSerializer(user).data, 'tokens': make_tokens(user)})
        return Response(s.errors, status=401)


class LogoutView(APIView):
    def post(self, request):
        try:
            RefreshToken(request.data.get('refresh', '')).blacklist()
            return Response({'message': 'Logged out.'})
        except TokenError:
            return Response({'error': 'Invalid token.'}, status=400)


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
    def patch(self, request):
        s = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(UserSerializer(request.user).data)
        return Response(s.errors, status=400)


class ProfilePhotoView(APIView):
    def post(self, request):
        f = request.FILES.get('photo')
        if not f:
            return Response({'error': 'No photo provided.'}, status=400)
        if not f.content_type.startswith('image/'):
            return Response({'error': 'File must be an image.'}, status=400)
        request.user.profile_photo = f
        request.user.save()
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    def post(self, request):
        s = ChangePasswordSerializer(data=request.data, context={'request': request})
        if s.is_valid():
            request.user.set_password(s.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed.'})
        return Response(s.errors, status=400)


# ── Skills ────────────────────────────────────────────────────────────────────

class SkillsView(APIView):
    def get(self, request):
        return Response(UserSkillSerializer(UserSkill.objects.filter(user=request.user), many=True).data)
    def post(self, request):
        s = UserSkillSerializer(data=request.data)
        if s.is_valid():
            s.save(user=request.user)
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class SkillDetailView(APIView):
    def patch(self, request, pk):
        skill = get_object_or_404(UserSkill, pk=pk, user=request.user)
        s = UserSkillSerializer(skill, data=request.data, partial=True)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, pk):
        get_object_or_404(UserSkill, pk=pk, user=request.user).delete()
        return Response(status=204)


# ── Resume ────────────────────────────────────────────────────────────────────

class ResumeView(APIView):
    def get(self, request):
        try:
            return Response(ResumeSerializer(request.user.resume).data)
        except Resume.DoesNotExist:
            return Response({'error': 'No resume.'}, status=404)

    def post(self, request):
        f = request.FILES.get('file')
        if not f:
            return Response({'error': 'No file provided.'}, status=400)
        if not f.name.lower().endswith('.pdf'):
            return Response({'error': 'Only PDF accepted.'}, status=400)
        try:
            r = request.user.resume
            r.file = f; r.original_filename = f.name; r.save()
        except Resume.DoesNotExist:
            r = Resume.objects.create(user=request.user, file=f, original_filename=f.name)
        return Response(ResumeSerializer(r).data)

    def delete(self, request):
        try:
            request.user.resume.delete()
            return Response(status=204)
        except Resume.DoesNotExist:
            return Response({'error': 'No resume.'}, status=404)


# ── OAuth ─────────────────────────────────────────────────────────────────────

def _get_or_create_user(email, defaults):
    """Get or create user, handling username collision."""
    email = email.lower().strip()
    try:
        user = User.objects.get(email=email)
        return user, False
    except User.DoesNotExist:
        base = defaults.get('username', email.split('@')[0])[:40]
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        defaults['username'] = username
        return User.objects.create_user(email=email, password=None, **defaults), True


class GoogleOAuthView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri', f"{settings.FRONTEND_URL}/oauth/google")
        if not code:
            return Response({'error': 'Code required.'}, status=400)
        try:
            tr = requests.post('https://oauth2.googleapis.com/token', data={
                'code': code, 'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': redirect_uri, 'grant_type': 'authorization_code',
            }, timeout=10).json()
            at = tr.get('access_token')
            if not at:
                return Response({'error': tr.get('error_description', 'Token exchange failed.')}, status=400)
            info = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {at}'}, timeout=10).json()
            email = info.get('email')
            if not email:
                return Response({'error': 'No email from Google.'}, status=400)
            user, _ = _get_or_create_user(email, {
                'first_name': info.get('given_name',''),
                'last_name':  info.get('family_name',''),
                'google_id':  info.get('id',''),
                'email_verified': True,
            })
            user.google_id = info.get('id','')
            user.email_verified = True
            user.save()
            return Response({'user': UserSerializer(user).data, 'tokens': make_tokens(user)})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class GitHubOAuthView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code required.'}, status=400)
        try:
            tr = requests.post('https://github.com/login/oauth/access_token',
                headers={'Accept':'application/json'},
                data={'client_id': settings.GITHUB_CLIENT_ID,
                      'client_secret': settings.GITHUB_CLIENT_SECRET, 'code': code},
                timeout=10).json()
            at = tr.get('access_token')
            if not at:
                return Response({'error': tr.get('error_description', 'Token exchange failed.')}, status=400)
            hdrs = {'Authorization': f'token {at}'}
            gh   = requests.get('https://api.github.com/user', headers=hdrs, timeout=10).json()
            emails = requests.get('https://api.github.com/user/emails', headers=hdrs, timeout=10).json()
            email = next((e['email'] for e in emails if isinstance(e,dict) and e.get('primary')),
                         gh.get('email',''))
            if not email:
                return Response({'error': 'No email from GitHub.'}, status=400)
            name_parts = (gh.get('name') or '').split(' ', 1)
            user, _ = _get_or_create_user(email, {
                'username':   gh.get('login','')[:50],
                'first_name': name_parts[0] if name_parts else '',
                'last_name':  name_parts[1] if len(name_parts)>1 else '',
                'github_id':  str(gh.get('id','')),
                'github_url': gh.get('html_url',''),
                'bio':        gh.get('bio','') or '',
                'location':   gh.get('location','') or '',
            })
            user.github_id = str(gh.get('id',''))
            user.github_access_token = at
            user.github_url = gh.get('html_url', user.github_url)
            user.save()
            return Response({'user': UserSerializer(user).data, 'tokens': make_tokens(user)})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class LinkedInOAuthView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri', f"{settings.FRONTEND_URL}/oauth/linkedin")
        if not code:
            return Response({'error': 'Code required.'}, status=400)
        try:
            tr = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data={
                'grant_type':'authorization_code','code':code,'redirect_uri':redirect_uri,
                'client_id':settings.LINKEDIN_CLIENT_ID,'client_secret':settings.LINKEDIN_CLIENT_SECRET,
            }, timeout=10).json()
            at = tr.get('access_token')
            if not at:
                return Response({'error': 'LinkedIn token exchange failed.'}, status=400)
            hdrs = {'Authorization': f'Bearer {at}'}
            profile = requests.get('https://api.linkedin.com/v2/me', headers=hdrs, timeout=10).json()
            ed = requests.get('https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
                headers=hdrs, timeout=10).json()
            email = ed['elements'][0]['handle~']['emailAddress']
            user, _ = _get_or_create_user(email, {
                'first_name': profile.get('localizedFirstName',''),
                'last_name':  profile.get('localizedLastName',''),
                'linkedin_id': str(profile.get('id','')),
            })
            user.linkedin_id = str(profile.get('id',''))
            user.linkedin_access_token = at
            user.save()
            return Response({'user': UserSerializer(user).data, 'tokens': make_tokens(user)})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
