from django.contrib import admin
from django.utils.html import format_html
from .models import Portfolio, PortfolioSection, Project, Experience, Education


class PortfolioSectionInline(admin.TabularInline):
    model  = PortfolioSection
    extra  = 0
    fields = ('section_type','title','is_visible','order')


class ProjectInline(admin.TabularInline):
    model  = Project
    extra  = 0
    fields = ('title','language','stars','is_featured','order')


class ExperienceInline(admin.TabularInline):
    model  = Experience
    extra  = 0
    fields = ('position','company','start_date','is_current')


class EducationInline(admin.TabularInline):
    model  = Education
    extra  = 0
    fields = ('degree','institution','start_year','is_current')


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display  = ('title','user','template_badge','status_badge','view_count','updated_at')
    list_filter   = ('is_published','template')
    search_fields = ('title','user__email','user__username')
    readonly_fields = ('id','created_at','updated_at','public_url_link')
    inlines       = [PortfolioSectionInline, ProjectInline, ExperienceInline, EducationInline]

    fieldsets = (
        ('Info',  {'fields': ('id','user','title','slug','tagline','template','is_published','public_url_link')}),
        ('Theme', {'fields': ('primary_color','secondary_color','background_color','text_color','font_family','dark_mode')}),
        ('Meta',  {'fields': ('created_at','updated_at'), 'classes': ('collapse',)}),
    )

    def template_badge(self, obj):
        colors = {'professional':'#6366f1','modern':'#8b5cf6','creative':'#f43f5e','tech':'#06b6d4','minimal':'#71717a'}
        c = colors.get(obj.template,'#888')
        return format_html('<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">{}</span>', c, obj.template.title())
    template_badge.short_description = 'Template'

    def status_badge(self, obj):
        if obj.is_published:
            return format_html('<span style="color:#34d399;font-weight:600">● Published</span>')
        return format_html('<span style="color:#94a3b8">○ Draft</span>')
    status_badge.short_description = 'Status'

    def view_count(self, obj):
        return obj.analytics.count()
    view_count.short_description = 'Views'

    def public_url_link(self, obj):
        url = f"http://localhost:3000{obj.public_url}"
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)
    public_url_link.short_description = 'Public URL'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display  = ('title','portfolio','language','stars','is_featured','is_github_repo')
    list_filter   = ('is_featured','is_github_repo','language')
    search_fields = ('title','portfolio__user__email','portfolio__title')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('position','company','portfolio','start_date','is_current')
    list_filter  = ('is_current',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree','institution','portfolio','start_year','is_current')
