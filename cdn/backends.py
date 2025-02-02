from storages.backends.s3boto3 import S3Boto3Storage

class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = 'screenplays'
    default_acl = 'public-read'

# to see if changings are being pushed to github