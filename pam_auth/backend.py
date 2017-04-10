import pam
from django.contrib.auth.models import User
import logging


class PamBackend(object):
    """
    The user running the application (the apache user on CentOS) 
    must be a member of the /etc/shadow group. 
    """
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
                logging.info("User %s logged in." % username)
            except User.DoesNotExist:
                # we don't care what the password is, as it won't be used.
                password = User.objects.make_random_password()
                user = User(username=username, password=password)
                user.save()
                logging.info("User %s was created." % username)
        else:
            logging.warning('User %s failed to log in. Code: %s Reason: %s' % (
                username, self._pam.code, self._pam.reason))
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
