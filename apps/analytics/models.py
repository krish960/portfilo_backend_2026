from django.db import models


class PortfolioView(models.Model):
    portfolio  = models.ForeignKey(
        'portfolios.Portfolio', on_delete=models.CASCADE, related_name='analytics'
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    referrer   = models.URLField(blank=True)
    viewed_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.portfolio} — {self.viewed_at:%Y-%m-%d %H:%M}"
