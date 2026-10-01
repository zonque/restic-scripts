import boto3
import os
import re

def restic_bucket():
    restic_repository = os.getenv("RESTIC_REPOSITORY")

    if restic_repository == None:
        raise RuntimeError("RESTIC_REPOSITORY environment variable must be set!")

    p = re.compile(r"s3:(https://s3\.([\w-]*).*)/(.*)")
    x = p.match(restic_repository)
    if not x:
        raise ValueError(f"Unrecognized RESTIC_REPOSITORY format: {restic_repository}")

    endpoint_url = x.group(1)
    region_name = x.group(2)
    bucket_name = x.group(3)

    s3 = boto3.resource('s3',
        region_name = region_name,
        endpoint_url = endpoint_url,
    )

    return s3.Bucket(bucket_name)
