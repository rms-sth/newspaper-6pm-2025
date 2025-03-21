from django.contrib import admin
from .models import Contact, Newsletter, Post, Category, Tag, UserProfile, Comment

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Newsletter)