# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=False, null=True, blank=True)

#     USERNAME_FIELD = "username"
#     REQUIRED_FIELDS = []  # createsuperuser will only ask for username

#     def __str__(self):
#         return self.username


# class UserQueryHistory(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     query = models.TextField()
#     response = models.TextField(blank=True, null=True)
#     tables_html = models.JSONField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.query[:40]}"



from django.db import models
from django.contrib.auth.models import User   # <-- Use default User

class UserQueryHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField(blank=True, null=True)
    tables_html = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.query[:40]}"
