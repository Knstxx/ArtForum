from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser, Role


UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio',)}),
)

admin.site.register(MyUser, UserAdmin)
admin.site.register(Role)
