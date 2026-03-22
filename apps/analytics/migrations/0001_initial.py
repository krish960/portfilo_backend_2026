import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('referrer', models.URLField(blank=True)),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='portfolios.portfolio')),
            ],
            options={'ordering': ['-viewed_at']},
        ),
    ]
