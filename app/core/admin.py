"""
# app/core/admin.py
Customizing Django User.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as translate

from . import models


class UserAdmin(BaseUserAdmin):
    """Define admin pages for users."""
    ordering = ["id"]
    list_display = ["email", "name"]
    fieldsets = (
        (None,                      {'fields': (
                                            'email',
                                            'password',
                                        )}),
        (translate('Permissions'), {'fields': (
                                            'is_active',
                                            'is_superuser',
                                            'is_staff',
                                        )}),
        (translate('Important Dates'), {'fields':
                                        (
                                            'last_login',
                                        )}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_superuser',
                'is_staff'
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
