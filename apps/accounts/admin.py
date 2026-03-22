from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserSkill, Resume


class UserSkillInline(admin.TabularInline):
    model   = UserSkill
    extra   = 1
    fields  = ('name', 'level', 'category', 'order')


class ResumeInline(admin.StackedInline):
    model      = Resume
    extra      = 0
    max_num    = 1
    fields     = ('file', 'original_filename', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('avatar_tag', 'email', 'username', 'full_name', 'is_active', 'is_staff', 'github_connected', 'portfolio_count', 'created_at')
    list_filter   = ('is_active', 'is_staff', 'is_superuser', 'email_verified')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering      = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'full_name', 'avatar_preview')
    inlines       = [UserSkillInline, ResumeInline]

    fieldsets = (
        ('Account',    {'fields': ('id', 'email', 'password', 'email_verified')}),
        ('Profile',    {'fields': ('avatar_preview', 'username', 'first_name', 'last_name', 'bio', 'location', 'phone', 'profile_photo')}),
        ('Social',     {'fields': ('github_url', 'linkedin_url', 'twitter_url', 'website_url')}),
        ('OAuth IDs',  {'fields': ('google_id', 'github_id', 'linkedin_id'), 'classes': ('collapse',)}),
        ('Permissions',{'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'username', 'password1', 'password2')}),
    )

    def avatar_tag(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="32" height="32" style="border-radius:50%;object-fit:cover"/>', obj.profile_photo.url)
        letter = (obj.first_name[:1] or obj.username[:1]).upper()
        return format_html('<div style="width:32px;height:32px;border-radius:50%;background:#6366f1;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:13px">{}</div>', letter)
    avatar_tag.short_description = ''

    def avatar_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="80" height="80" style="border-radius:12px;object-fit:cover"/>', obj.profile_photo.url)
        return '—'
    avatar_preview.short_description = 'Photo'

    def github_connected(self, obj):
        if obj.github_id:
            return format_html('<span style="color:#34d399">● Connected</span>')
        return format_html('<span style="color:#94a3b8">○ —</span>')
    github_connected.short_description = 'GitHub'

    def portfolio_count(self, obj):
        count = obj.portfolios.count()
        return format_html('<b>{}</b>', count)
    portfolio_count.short_description = 'Portfolios'


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display  = ('user', 'name', 'level_bar', 'category', 'order')
    list_filter   = ('category',)
    search_fields = ('name', 'user__email', 'user__username')

    def level_bar(self, obj):
        color = '#34d399' if obj.level >= 80 else '#fbbf24' if obj.level >= 50 else '#f87171'
        return format_html(
            '<div style="background:#e2e8f0;border-radius:4px;width:120px;height:10px">'
            '<div style="background:{};width:{}%;height:100%;border-radius:4px"></div></div> {}%',
            color, obj.level, obj.level
        )
    level_bar.short_description = 'Level'


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'original_filename', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
