from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class FileDescriptor(models.Model):
    """
    A wrapper around the status and path of a file that allows the status to
    be remembered for display to the user.

    There is an assumption in this model that each file's path will always be
    unique. In order for this to be true the agrf can't recycle file names.
    TODO: check if this is indeed the case. If it's not some confusion will
    occur!
    """
    NEW = 1  # This is the first time we have seen the file
    PENDING_UPLOAD = 2  # The file has been marked for upload/is being uploaded
    UPLOADED = 3  # The file has successfully been uploaded
    FAILED_UPLOAD = 4  # Something went wrong - the file wasn't uploaded

    FILE_STATUS = (
        (NEW, 'New'),
        (PENDING_UPLOAD, 'Pending Upload'),
        (UPLOADED, 'Uploaded'),
        (FAILED_UPLOAD, 'Upload Failed')
    )

    # path is what we will be using to look up the instances
    path = models.CharField(max_length=244, db_index=True)
    exported = models.SmallIntegerField(
        choices=FILE_STATUS,
        default=NEW)

    def __str__(self):
        return '%s %s' % (self.path, self.exported)

    class Meta:
        ordering = ['path']

    def set_uploading(self):
        """
        Sets the exported status flag to PENDING_UPLOAD.
        Does not save the change!
        """
        self.exported = self.PENDING_UPLOAD

    def set_uploaded(self):
        """
        Sets the exported status flag to UPLOADED.
        Does not save the change!
        """
        self.exported = self.UPLOADED

    def set_failed_upload(self):
        """
        Sets the exported status flag to FAILED_UPLOAD.
        Does not save the change!
        """
        self.exported = self.FAILED_UPLOAD

    @staticmethod
    def get_status(path):
        """
        :param path: The path of the file whose status is desired.
        :return: A string giving the file status. If no file found, then
                 the FileDescriptor.NEW status string
        """
        try:
            fd = FileDescriptor.objects.get(path=path)
            return fd.get_exported_display()
        except ObjectDoesNotExist:
            for candidate in FileDescriptor.FILE_STATUS:
                if candidate[0] == FileDescriptor.NEW:
                    return candidate[1]
            raise  # should not get here...

    @classmethod
    def get_file_descriptor_for(cls, path):
        """
        :param path: The path to the file whose descriptor instance is desired
        :return: The file descriptor for the path. If it doesn't exist, it is
                 created (but the new instance is not saved).
        """
        try:
            return cls.objects.get(path=path)
        except ObjectDoesNotExist:
            return cls(path=path, exported=cls.NEW)
