"""
Delete files from the AWS S3 buckets
"""
import boto3
from django.conf import settings

s3_resource = boto3.resource(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def show_or_delete_from_bucket(bucket_name, delete_it=False)

    bucket = s3_resource.Bucket(bucket_name)

    for obj in bucket.objects.all():
        print obj
        if delete_it is True:
            obj.delete()


if __name__ == '__main__':
    show_or_delete_from_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    show_or_delete_from_bucket(settings.AWS_STORAGE_BUCKET_NAME, delete_it=True)
    show_or_delete_from_bucket(settings.AWS_STORAGE_BUCKET_NAME)
