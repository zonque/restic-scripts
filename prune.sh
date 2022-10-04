#!/bin/sh

set -e

RESTIC_REPOSITORY=$1
RESTIC_PASSWORD=$2

if [ -z "$RESTIC_PASSWORD" ]; then
    echo "Usage: $0 <repo> <password>"
    exit 1
fi

if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "AWS_ACCESS_KEY_ID must be set in environment"
    exit 1
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "AWS_SECRET_ACCESS_KEY must be set in environment"
    exit 1
fi

export RESTIC_REPOSITORY
export RESTIC_PASSWORD

echo "========== $RESTIC_REPOSITORY =========="

python3 check-versions.py check

# 90 days is the minimum retention time in Wasabi
restic forget --prune --keep-within 90d

python3 check-versions.py prune

echo "========== done. =========="
