from django.db import models
from django.contrib.auth.models import User   # <-- Use default User

class UserQueryHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField(blank=True, null=True)
    tables_html = models.JSONField(blank=True, null=True)
    chart_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.query[:40]}"
