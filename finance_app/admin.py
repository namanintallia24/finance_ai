from django.contrib import admin
from .models import UserQueryHistory  # or any of your custom models

# Register your own models here
admin.site.register(UserQueryHistory)
