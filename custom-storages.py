from django.conf import settings
from storages.backends.s3boto3 import S3BotoStorage


class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3BotoStorage):
<<<<<<< HEAD
    location = settings.MEDIAFILES_LOCATION
=======
    location = settings.MEDIAFILES_LOCATION
>>>>>>> eb0c8d1755aa19e19e60827d232843989edf756c
