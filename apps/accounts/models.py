from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('email_verified', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email         = models.EmailField(unique=True)
    username      = models.CharField(max_length=50, unique=True)
    first_name    = models.CharField(max_length=100, blank=True)
    last_name     = models.CharField(max_length=100, blank=True)
    bio           = models.TextField(blank=True)
    location      = models.CharField(max_length=200, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    phone         = models.CharField(max_length=20, blank=True)
    github_url    = models.URLField(blank=True)
    linkedin_url  = models.URLField(blank=True)
    twitter_url   = models.URLField(blank=True)
    website_url   = models.URLField(blank=True)
    github_access_token    = models.TextField(blank=True)
    linkedin_access_token  = models.TextField(blank=True)
    google_id    = models.CharField(max_length=200, blank=True)
    github_id    = models.CharField(max_length=200, blank=True)
    linkedin_id  = models.CharField(max_length=200, blank=True)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table  = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} (@{self.username})"

    @property
    def full_name(self):
        n = f"{self.first_name} {self.last_name}".strip()
        return n or self.username


class UserSkill(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    name     = models.CharField(max_length=100)
    level    = models.IntegerField(default=80)
    category = models.CharField(max_length=50, blank=True)
    order    = models.IntegerField(default=0)

    class Meta:
        ordering     = ['order', 'name']
        verbose_name = 'Skill'

    def __str__(self):
        return f"{self.user.username} — {self.name} ({self.level}%)"


class Resume(models.Model):
    user              = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume')
    file              = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255)
    uploaded_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Resume'

    def __str__(self):
        return f"{self.user.username} — {self.original_filename}"
