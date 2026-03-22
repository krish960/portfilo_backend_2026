import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(blank=True, max_length=100)),
                ('tagline', models.CharField(blank=True, max_length=300)),
                ('template', models.CharField(choices=[('professional', 'Professional'), ('modern', 'Modern'), ('creative', 'Creative'), ('tech', 'Tech'), ('minimal', 'Minimal')], default='professional', max_length=50)),
                ('is_published', models.BooleanField(default=False)),
                ('primary_color', models.CharField(default='#6366f1', max_length=7)),
                ('secondary_color', models.CharField(default='#8b5cf6', max_length=7)),
                ('background_color', models.CharField(default='#ffffff', max_length=7)),
                ('text_color', models.CharField(default='#1f2937', max_length=7)),
                ('font_family', models.CharField(choices=[('inter', 'Inter'), ('playfair', 'Playfair Display'), ('roboto', 'Roboto'), ('poppins', 'Poppins'), ('fira', 'Fira Code')], default='inter', max_length=50)),
                ('dark_mode', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolios', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-updated_at']},
        ),
        migrations.CreateModel(
            name='PortfolioSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_type', models.CharField(choices=[('about', 'About Me'), ('skills', 'Skills'), ('projects', 'Projects'), ('education', 'Education'), ('experience', 'Experience'), ('contact', 'Contact'), ('social', 'Social Links')], max_length=50)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('is_visible', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='portfolios.portfolio')),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('tech_stack', models.JSONField(default=list)),
                ('live_url', models.URLField(blank=True)),
                ('github_url', models.URLField(blank=True)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='project_thumbnails/')),
                ('is_featured', models.BooleanField(default=False)),
                ('is_github_repo', models.BooleanField(default=False)),
                ('github_repo_id', models.CharField(blank=True, max_length=100)),
                ('stars', models.IntegerField(default=0)),
                ('language', models.CharField(blank=True, max_length=50)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='portfolios.portfolio')),
            ],
            options={'ordering': ['order', '-created_at']},
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=200)),
                ('position', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_current', models.BooleanField(default=False)),
                ('company_url', models.URLField(blank=True)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('order', models.IntegerField(default=0)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='portfolios.portfolio')),
            ],
            options={'ordering': ['order', '-start_date']},
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=200)),
                ('degree', models.CharField(max_length=200)),
                ('field_of_study', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('start_year', models.IntegerField()),
                ('end_year', models.IntegerField(blank=True, null=True)),
                ('is_current', models.BooleanField(default=False)),
                ('gpa', models.CharField(blank=True, max_length=10)),
                ('order', models.IntegerField(default=0)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='portfolios.portfolio')),
            ],
            options={'ordering': ['order', '-start_year']},
        ),
        migrations.AlterUniqueTogether(
            name='portfolio',
            unique_together={('user', 'slug')},
        ),
        migrations.AlterUniqueTogether(
            name='portfoliosection',
            unique_together={('portfolio', 'section_type')},
        ),
    ]
