from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Title, Genre, Category, Comment, Review


UserAdmin.fieldsets += (('Extra Fields', {'fields': ('bio', 'role')}),)

admin.site.register(Title)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Review)
