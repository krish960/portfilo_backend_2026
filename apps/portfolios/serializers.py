from rest_framework import serializers
from .models import Portfolio, PortfolioSection, Project, Experience, Education


class PortfolioSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PortfolioSection
        fields = ['id', 'section_type', 'title', 'is_visible', 'order']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Project
        fields = [
            'id', 'title', 'description', 'tech_stack', 'live_url',
            'github_url', 'thumbnail', 'is_featured', 'is_github_repo',
            'github_repo_id', 'stars', 'language', 'order', 'created_at',
        ]
        read_only_fields = ['created_at']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Experience
        fields = [
            'id', 'company', 'position', 'description', 'start_date',
            'end_date', 'is_current', 'company_url', 'location', 'order',
        ]


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Education
        fields = [
            'id', 'institution', 'degree', 'field_of_study', 'description',
            'start_year', 'end_year', 'is_current', 'gpa', 'order',
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    sections    = PortfolioSectionSerializer(many=True, read_only=True)
    projects    = ProjectSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    educations  = EducationSerializer(many=True, read_only=True)
    public_url  = serializers.CharField(read_only=True)
    owner       = serializers.SerializerMethodField()

    class Meta:
        model  = Portfolio
        fields = [
            'id', 'title', 'slug', 'tagline', 'template', 'is_published',
            'primary_color', 'secondary_color', 'background_color', 'text_color',
            'font_family', 'dark_mode',
            'sections', 'projects', 'experiences', 'educations',
            'public_url', 'owner', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_owner(self, obj):
        from apps.accounts.serializers import UserSerializer
        return UserSerializer(obj.user).data


class PortfolioListSerializer(serializers.ModelSerializer):
    public_url = serializers.CharField(read_only=True)
    view_count = serializers.SerializerMethodField()

    class Meta:
        model  = Portfolio
        fields = [
            'id', 'title', 'slug', 'tagline', 'template', 'is_published',
            'primary_color', 'public_url', 'view_count', 'created_at', 'updated_at',
        ]

    def get_view_count(self, obj):
        return obj.analytics.count()


class CreatePortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Portfolio
        fields = ['title', 'tagline', 'template', 'primary_color', 'secondary_color', 'font_family']

    def create(self, validated_data):
        user      = self.context['request'].user
        portfolio = Portfolio.objects.create(user=user, **validated_data)
        # Auto-create all 7 default sections
        default_sections = [
            ('about',      'About Me',    0),
            ('skills',     'Skills',      1),
            ('projects',   'Projects',    2),
            ('experience', 'Experience',  3),
            ('education',  'Education',   4),
            ('contact',    'Contact',     5),
            ('social',     'Social Links',6),
        ]
        PortfolioSection.objects.bulk_create([
            PortfolioSection(
                portfolio=portfolio,
                section_type=st,
                title=title,
                order=order,
            )
            for st, title, order in default_sections
        ])
        return portfolio
