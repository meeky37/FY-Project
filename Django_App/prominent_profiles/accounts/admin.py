from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'phone_number', 'date_of_birth', 'email_verified', 'location', 'is_active', 'is_staff')
    search_fields = ('email', 'phone_number', 'date_of_birth', 'location')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('phone_number', 'date_of_birth', 'email_verified', 'location')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone_number', 'date_of_birth', 'email_verified', 'location'),
        }),
    )

admin.site.register(CustomUser, UserAdmin)
