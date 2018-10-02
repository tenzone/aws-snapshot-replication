# AWS Snapshot Replicator

## Replicate.py

this script will run nightly, and pull all snapshot id's from us-east-1 that have the tag `awsbackup` applied. It will then replicate them to us-west-2.  These can be leveraged later on to restore file's or serve as a DR snapshot to be converted to an AMI.

## Cleanup30.py
This script will search for copied snapshots that are over 30 days old, and remove them