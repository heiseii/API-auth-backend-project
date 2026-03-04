from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, Permission


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username", "is_active", "is_staff", "failed_attempts", "locked_until"]
    list_filter = ["is_active", "is_staff", "roles"]
    search_fields = ["email", "username"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name")}),
        ("Roles", {"fields": ("roles",)}),
        ("Permisos Django", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Seguridad", {"fields": ("failed_attempts", "locked_until", "last_login_ip")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "created_at"]
    search_fields = ["name"]
    filter_horizontal = ["permissions"]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "codename", "description"]
    search_fields = ["name", "codename"]