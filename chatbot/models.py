from django.db import models
from django.utils import timezone
from datetime import timedelta

class ConversationQuota(models.Model):
    conversation_id = models.CharField(max_length=255, primary_key=True)
    quota_used = models.IntegerField(default=0)
    last_reset = models.DateTimeField(default=timezone.now)

    def increment_quota(self):
        """Increment quota and reset if it's a new day"""
        now = timezone.now()
        if now - self.last_reset > timedelta(days=1):
            self.quota_used = 1
            self.last_reset = now
        else:
            self.quota_used += 1
        self.save()

    def get_remaining_quota(self, daily_limit=10):
        """Get remaining quota for the day"""
        now = timezone.now()
        if now - self.last_reset > timedelta(days=1):
            return daily_limit
        return max(0, daily_limit - self.quota_used)

    class Meta:
        db_table = 'conversation_quota'
        verbose_name = 'Conversation Quota'
        verbose_name_plural = 'Conversation Quotas'

    def __str__(self):
        return f"Conversation {self.conversation_id} - Used: {self.quota_used}"
