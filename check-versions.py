import logging
import os
import sys

from bucket import restic_bucket

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} [check|prune]")
    os._exit(1)

cmd = sys.argv[1]

if not cmd in ['check', 'prune']:
    print(f"Usage: {sys.argv[0]} [check|prune]")
    os._exit(1)

# boto3.set_stream_logger('', logging.DEBUG)

b = restic_bucket()

objects = [f.key for f in b.objects.all()]

print(f"Repository bucket has {len(objects)} objects")

object_versions = {}
delete_objects = []
check_failed = False

for version in b.object_versions.all():
    k = version.object_key

    if cmd == "prune":
        if not k in objects:
            print(f"Deleting object version {version.id} of non-existing object {k}")
            delete_objects.append({ 'Key': k, 'VersionId': version.id })

    if cmd == "check":
        if k.startswith("locks/"):
            continue

        if k in object_versions:
            print(f"{k} has more than one version!")
            check_failed = True

        object_versions[k] = version.id

if len(delete_objects) > 0:
    print(f"Purging {len(delete_objects)} object versions ...")

    b.delete_objects(
        Delete={
            'Objects': delete_objects,
            'Quiet': True
        }
    )

if check_failed:
    print("Check failed")
    os._exit(1)
