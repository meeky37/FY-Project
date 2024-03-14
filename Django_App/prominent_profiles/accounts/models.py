from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from profiles_app.models import Entity


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for CustomUser, providing helper methods to create user and superuser
    accounts.

    # create_user: Creates and returns a new user
    # create_superuser: Creates and returns a new superuser with all permissions.
    """
    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    The model uses 'email' as the USERNAME_FIELD and requires 'phone_number', 'date_of_birth',
    'location', 'first_name', and 'last_name' for creating a user.
    CustomUserManager (above) is used for objects creation.
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    last_visit = models.DateTimeField(null=True, blank=True)
    last_visit_excluding_today = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'date_of_birth', 'location', 'first_name', 'last_name']

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """
    Each Subscription links a CustomUser instance to an Entity instance,
    enabling the persistence of user subs to various entities within Prominent Profiles across
    devices.
    Enforces uniqueness to ensure each user-entity pair is only subscribed once.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'entity')
