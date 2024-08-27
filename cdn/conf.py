import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "episodeone"
AWS_S3_ENDPOINT_URL = "https://sfo3.digitaloceanspaces.com"
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "https://episodeone.sfo3.digitaloceanspaces.com"

# Static and Media settings
DEFAULT_FILE_STORAGE = "cdn.backends.MediaRootS3Boto3Storage"
STATICFILES_STORAGE = "cdn.backends.StaticRootS3Boto3Storage"
AWS_MEDIA_LOCATION = 'media'
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_MEDIA_LOCATION}/'
STATIC_URL = f'{AWS_S3_ENDPOINT_URL}/static/'
