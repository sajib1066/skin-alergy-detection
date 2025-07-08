from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ScanHistory(models.Model):
    """Model to store scan history for users"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='scan_history'
    )
    image = models.ImageField(
        upload_to='scan_images/', null=True, blank=True
    )
    scan_date = models.DateTimeField(default=timezone.now)

    # Detection results stored as JSON
    allergy_type = models.CharField(max_length=100)
    confidence = models.FloatField()
    treatment = models.TextField()

    class Meta:
        ordering = ['-scan_date']
        verbose_name_plural = 'Scan History'

    def __str__(self):
        return (f"{self.user.email} - {self.allergy_type} "
                f"({self.scan_date.strftime('%Y-%m-%d %H:%M')})")
