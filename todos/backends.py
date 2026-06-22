from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    """
    Authentication backend that allows users to log in using their email
    address instead of their username.

    Django's default backend uses `username`. This backend looks up the user
    by `email` and delegates the password check to the parent class.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # `username` here holds whatever was typed in the login field (the email).
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            # Run the default hasher to mitigate timing attacks
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
