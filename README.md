# Support scripts for Restic on S3

With [Restic](https://restic.readthedocs.io) backups on [S3](https://en.wikipedia.org/wiki/Amazon_S3),
some configuration is needed to make the setup tamper-proof.

## S3 configuration

The user credentials stored on the host running the backups should have a policy in place
that only allows `GetObject` and `PutObject` bucket-wide, and `DeleteObject` for objects
in the `locks/` folder:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::BUCKETNAME",
        "arn:aws:s3:::BUCKETNAME/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "s3:DeleteObject",
      "Resource": "arn:aws:s3:::BUCKETNAME/locks/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::BUCKETNAME"
    }
  ]
}
```

However, even with the above policy in place, an attacker that obtains the credentials
can still overwrite objects in the bucket, as creating and replacing an object in S3 is
both covered by the `PutObject` action.

Hence, S3 buckets that hold Restic backups should be configured to have object versioning
enabled. This way, objects that are overwritten can be recovered. This however has the
side-effect that files can no longer be fully deleted by prunes.

# Scripts

All scripts require `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` to be set in the environment.

## Check

When called with the `check` argument, the `check-versions.py` script traverses through the
given bucket (passed in the `RESTIC_REPOSITORY` environment variable) and finds all objects
that have more than one version. This might be an indicaton for an attempt to tamper with the
files. Objects with a prefix of `/locks` are ignored.

If any such object is found, the script will exit with code 1.

## Prune

As described above, a simple `restic prune` will not free up the space in S3, as the
objects are merely marked for deletion due to the bucket versioning logic.

When called with the `prune` argument, the `check-versions.py` script traverses through the
given bucket (passed in the `RESTIC_REPOSITORY` environment variable) and finds all deleted
objects that have versions and deletes them. This will then free up the space in the storage
provider.

## Umbrella script for pruning

`prune.sh` is a script that must be called with a restic repository URL as 1st and the corresponding
password as the 2nd argument. It will then first check for signs of tampering, the call `restic prune`
and eventually `check-version.py prune` to complete the work.

## Sanity check

`check-snapshot.py` takes a Restic URL as argument and scans the snapshots in the bucket.

It then performs two checks:

* Assert that the number of snapshots taken in the last 48h is twice the amount than the number
  of snapshots in the last 24h. This way, anomalities in backup behaviour can be detected
* Assert that there was at least one snapshot taken within the last 24h.
