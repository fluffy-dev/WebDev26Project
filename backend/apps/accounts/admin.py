from django.contrib import admin
from .models import Avatar, Profile


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_at"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "total_score", "virtual_currency", "best_wpm", "avatar"]
    list_select_related = ["user", "avatar"]
