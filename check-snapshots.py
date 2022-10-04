import logging
import os

from datetime import datetime, timedelta, timezone
from bucket import restic_bucket

# boto3.set_stream_logger('', logging.DEBUG)

b = restic_bucket()

snapshots = []

for version in b.object_versions.filter(Prefix="snapshots/"):
    k = version.object_key
    obj = version.get()
    date = obj.get('LastModified')
    snapshots.append(date)

past_24h = list(filter(lambda d: d > datetime.now(timezone.utc) - timedelta(days=1), snapshots))
past_48h = list(filter(lambda d: d > datetime.now(timezone.utc) - timedelta(days=2), snapshots))

if len(past_24h) == 0:
    print(f"No backups in the last 24h!")
    os._exit(1)

if len(past_48h) != 2 * len(past_24h):
    print(f"{len(past_24h)} backups in the last 24h but {len(past_48h)} backups in the last 48h!")
    os._exit(1)

print(f"Passed. {len(past_24h)} snapshots within the last 24h")