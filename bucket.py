import boto3
import os
import re

def restic_bucket():
    restic_repository = os.getenv("RESTIC_REPOSITORY")

    if restic_repository == None:
        raise("RESTIC_REPOSITORY environment variable must be set!")

    p = re.compile("s3:(https://s3\.([\w-]*).*)/(.*)")
    x = p.match(restic_repository)

    endpoint_url = x.group(1)
    region_name = x.group(2)
    bucket_name = x.group(3)

    s3 = boto3.resource('s3',
        region_name = region_name,
        endpoint_url = endpoint_url,
    )

    return s3.Bucket(bucket_name)
