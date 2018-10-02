#!/usr/bin/env python3

import boto3
from datetime import datetime, timedelta, tzinfo

client = boto3.client('ec2', region_name='us-west-2')

snaps = client.describe_snapshots(
    Filters=[
        {
            'Name': 'tag:identifier',
            'Values': ['awsbackup',]
        },
    ],)

sortsnap = sorted(snaps['Snapshots'], key=lambda x: x['StartTime'])
retention_period = datetime.now().date() - timedelta(days=30)


for snap in sortsnap:
    tagdict = snap['Tags']
    name_tag = [i for i,_ in enumerate(tagdict) if _['Key'] == 'Name'][0]
            
    if snap['StartTime'].date() < retention_period:
        client.delete_snapshot(
            SnapshotId=f"{snap['SnapshotId']}"
        )
        print(f"Deleting {str(snap['Tags'][name_tag]['Value'])} {str(snap['SnapshotId'])}")
