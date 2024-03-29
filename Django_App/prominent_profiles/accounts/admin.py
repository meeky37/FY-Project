from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Subscription


class UserAdmin(BaseUserAdmin):
    """
    Provides an appropriate list view of entities.
    Enables search based on many factors for easy user look up.
    """

    list_display = (
    'email', 'phone_number', 'date_of_birth', 'email_verified', 'location', 'first_name',
    'last_name', 'is_active', 'is_staff')
    search_fields = (
    'email', 'phone_number', 'date_of_birth', 'location', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'last_visit', 'last_visit_excluding_today')}),
        ('Personal info', {'fields': (
        'phone_number', 'date_of_birth', 'email_verified', 'location', 'first_name', 'last_name')}),
        ('Permissions',
         {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        # ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'password1', 'password2', 'phone_number', 'date_of_birth', 'email_verified',
            'location', 'first_name', 'last_name'),
        }),
    )


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Subscription)
