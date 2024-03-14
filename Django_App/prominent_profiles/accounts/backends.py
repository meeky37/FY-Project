from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailPhoneBackend(ModelBackend):
    def authenticate(self, request, phone_number=None, username=None, password=None, **kwargs):
        try:
            print(username)
            user = User.objects.get(
                Q(email__iexact=username) | Q(phone_number__iexact=phone_number)
            )
            # If the password is correct, return the user object
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
