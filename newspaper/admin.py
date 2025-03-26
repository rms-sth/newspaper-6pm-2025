from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import Contact, Newsletter, Post, Category, Tag, UserProfile, Comment

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Newsletter)


class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ("content",)


admin.site.register(Post, PostAdmin)
