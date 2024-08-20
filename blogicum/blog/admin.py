from django.contrib import admin

from .models import Category, Post, Location, Comment

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Location)
admin.site.register(Comment)
