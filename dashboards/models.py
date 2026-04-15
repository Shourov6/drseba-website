from django.conf import settings
from django.db import models


class AdminNotification(models.Model):
    """Persistent notifications for super admin dashboard."""

    TYPE_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    ]

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_notifications',
    )
    source_key = models.CharField(max_length=120)
    title = models.CharField(max_length=120)
    message = models.TextField()
    notif_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='info')
    target_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('admin_user', 'source_key')
        indexes = [
            models.Index(fields=['admin_user', 'is_read']),
            models.Index(fields=['admin_user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({'read' if self.is_read else 'unread'})"
