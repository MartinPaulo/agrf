import pam
from django.contrib.auth.models import User


class PamBackend(object):
    _pam = pam.pam()

    def authenticate(self, username=None, password=None):
        """
        All users that are recognized by the operating system will be returned
        (or created, then returned).
        """
        user = None
        # If the user is authenticated by the operating system then...
        if self._pam.authenticate(username, password):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                password = User.objects.make_random_password()
                user = User(username=username, password=password)
                user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
