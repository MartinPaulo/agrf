from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class FileDescriptor(models.Model):
    owner = models.ForeignKey(User, editable=False)
    path = models.CharField(max_length=244)
    exported = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s %s' % (self.owner, self.path)

    class Meta:
        ordering = ['owner', 'path']
