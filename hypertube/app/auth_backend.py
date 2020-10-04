from .models import User 
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class PasswordlessAuthBackend(ModelBackend):
    """Log in to Django without providing a password.

    """
    def authenticate(self, request, username=None, password=None):
        # user = User.objects.filter(username=login_name)
        if username is None:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username)
        return user
        # try:
        #     return User.objects.get(username=username)
        # except User.DoesNotExist:
        #     return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None