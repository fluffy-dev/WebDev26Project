"""Django admin configuration for the users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .infrastructure.models import ProfileImage, User


@admin.register(ProfileImage)
class ProfileImageAdmin(admin.ModelAdmin):
    """Admin panel for managing predefined profile images."""

    list_display = ("id", "image")
    readonly_fields = ("id",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin panel for user accounts."""

    list_display = ("username", "email", "is_staff", "created_at")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("profile",)}),
    )
