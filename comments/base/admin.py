from django.contrib import admin
from .models import UserProfile, BlogPost, Subscription

admin.site.register(UserProfile)
admin.site.register(BlogPost)
admin.site.register(Subscription)
