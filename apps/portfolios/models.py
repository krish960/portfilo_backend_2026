import re
import uuid
from django.db import models
from django.conf import settings

TEMPLATE_CHOICES = [
    ('professional', 'Professional'),
    ('modern',       'Modern'),
    ('creative',     'Creative'),
    ('tech',         'Tech'),
    ('minimal',      'Minimal'),
]

SECTION_TYPES = [
    ('about',      'About Me'),
    ('skills',     'Skills'),
    ('projects',   'Projects'),
    ('education',  'Education'),
    ('experience', 'Experience'),
    ('contact',    'Contact'),
    ('social',     'Social Links'),
]

FONT_CHOICES = [
    ('inter',    'Inter'),
    ('playfair', 'Playfair Display'),
    ('roboto',   'Roboto'),
    ('poppins',  'Poppins'),
    ('fira',     'Fira Code'),
]


class Portfolio(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    title            = models.CharField(max_length=200)
    slug             = models.CharField(max_length=120, blank=True)
    tagline          = models.CharField(max_length=300, blank=True)
    template         = models.CharField(max_length=50, choices=TEMPLATE_CHOICES, default='professional')
    is_published     = models.BooleanField(default=False)
    primary_color    = models.CharField(max_length=7, default='#6366f1')
    secondary_color  = models.CharField(max_length=7, default='#8b5cf6')
    background_color = models.CharField(max_length=7, default='#ffffff')
    text_color       = models.CharField(max_length=7, default='#1f2937')
    font_family      = models.CharField(max_length=50, choices=FONT_CHOICES, default='inter')
    dark_mode        = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        # ──────────────────────────────────────────────────────────────────────
        # NOTE: slug must be unique per user (two portfolios of same user
        # cannot share a slug), but different users CAN have the same slug.
        # ──────────────────────────────────────────────────────────────────────
        unique_together = ['user', 'slug']
        ordering        = ['-updated_at']
        verbose_name    = 'Portfolio'

    def __str__(self):
        return f"{self.user.username} / {self.title}"

    # ── slug generation ───────────────────────────────────────────────────────

    def _make_unique_slug(self):
        """
        Produce a URL-safe slug that is unique for this user.

        Strategy:
          1st portfolio  →  <username>          e.g. "john"
          2nd portfolio  →  <username>-2        e.g. "john-2"
          3rd portfolio  →  <username>-3        e.g. "john-3"
          …and so on.

        This never collides because we keep incrementing the counter until
        a free slot is found.
        """
        base = re.sub(r'[^a-z0-9]+', '-', self.user.username.lower()).strip('-')
        if not base:
            base = 'portfolio'

        candidate = base
        counter   = 2
        qs = Portfolio.objects.filter(user=self.user)
        if self.pk:                         # exclude self on updates
            qs = qs.exclude(pk=self.pk)

        while qs.filter(slug=candidate).exists():
            candidate = f"{base}-{counter}"
            counter  += 1

        return candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._make_unique_slug()
        super().save(*args, **kwargs)

    # ── helpers ───────────────────────────────────────────────────────────────

    @property
    def public_url(self):
        """Frontend route that renders this portfolio publicly."""
        return f"/p/{self.slug}"


# ── Portfolio sections ────────────────────────────────────────────────────────

class PortfolioSection(models.Model):
    portfolio    = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    title        = models.CharField(max_length=200, blank=True)
    is_visible   = models.BooleanField(default=True)
    order        = models.IntegerField(default=0)

    class Meta:
        ordering        = ['order']
        unique_together = ['portfolio', 'section_type']
        verbose_name    = 'Section'

    def __str__(self):
        return f"{self.portfolio.title} — {self.section_type}"


# ── Projects ──────────────────────────────────────────────────────────────────

class Project(models.Model):
    portfolio      = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='projects')
    title          = models.CharField(max_length=200)
    description    = models.TextField(blank=True)
    tech_stack     = models.JSONField(default=list)
    live_url       = models.URLField(blank=True)
    github_url     = models.URLField(blank=True)
    thumbnail      = models.ImageField(upload_to='project_thumbnails/', blank=True, null=True)
    is_featured    = models.BooleanField(default=False)
    is_github_repo = models.BooleanField(default=False)
    github_repo_id = models.CharField(max_length=100, blank=True)
    stars          = models.IntegerField(default=0)
    language       = models.CharField(max_length=50, blank=True)
    order          = models.IntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


# ── Experience ────────────────────────────────────────────────────────────────

class Experience(models.Model):
    portfolio   = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='experiences')
    company     = models.CharField(max_length=200)
    position    = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date  = models.DateField()
    end_date    = models.DateField(null=True, blank=True)
    is_current  = models.BooleanField(default=False)
    company_url = models.URLField(blank=True)
    location    = models.CharField(max_length=200, blank=True)
    order       = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.position} at {self.company}"


# ── Education ─────────────────────────────────────────────────────────────────

class Education(models.Model):
    portfolio      = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='educations')
    institution    = models.CharField(max_length=200)
    degree         = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    description    = models.TextField(blank=True)
    start_year     = models.IntegerField()
    end_year       = models.IntegerField(null=True, blank=True)
    is_current     = models.BooleanField(default=False)
    gpa            = models.CharField(max_length=10, blank=True)
    order          = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_year']

    def __str__(self):
        return f"{self.degree} at {self.institution}"
