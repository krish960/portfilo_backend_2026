from django.db import models


class ContactMessage(models.Model):
    portfolio    = models.ForeignKey(
        'portfolios.Portfolio', on_delete=models.CASCADE, related_name='messages'
    )
    sender_name  = models.CharField(max_length=200)
    sender_email = models.EmailField()
    subject      = models.CharField(max_length=300, blank=True)
    message      = models.TextField()
    is_read      = models.BooleanField(default=False)
    sent_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"From {self.sender_name} → {self.portfolio.user.username}"
