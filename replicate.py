#!/usr/bin/env python3

import boto3
import concurrent.futures

#set variables for the boto/aws client
client = boto3.client('ec2', region_name='us-east-1')

#get snapshots that are tagged with the 'awsbackup' tag
snaps = client.describe_snapshots(
    Filters=[
        {
            'Name': 'tag:identifier',
            'Values': ['awsbackup',]
        },
    ],)

#sort the snapshots and get the latest time (should be yesterday)    
sortsnap = sorted(snaps['Snapshots'], key=lambda x: x['StartTime'])
snaptime = str(sortsnap[-1]['StartTime'])
latest_snaps = filter(lambda x: str(x['StartTime'])[0:10] == snaptime[0:10], sortsnap)
snaps_list = list(latest_snaps)


def replicatesnap(snap):
    #copy snapshots to the uswest2 region
    session = boto3.session.Session()
    clientwest = session.client('ec2', region_name='us-west-2')
    waiter = clientwest.get_waiter('snapshot_completed')
    response = clientwest.copy_snapshot(
        SourceSnapshotId=snap['SnapshotId'],
        SourceRegion='us-east-1',
        DestinationRegion='us-west-2',
        Description=f"Snap Copy from {snap['Description']}",
        DryRun=False
        )
    print(response)

    #get the replicated snapshot id, and copy the tags from the original snapshot
    newsnapid = response['SnapshotId']
    clientwest.create_tags(
        Resources = [newsnapid],
        Tags=snap['Tags']
    )
    #wait until the current snapshot is completed
    waiter.wait(
        SnapshotIds=[newsnapid],
        WaiterConfig={'Delay' : 60, 'MaxAttempts' : 120}    
        )
    
#tell the job to run 5 at a time, as 5 is the AWS limit for concurrent snapshot copies to a single region
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
    future_to_replicate = {executor.submit(replicatesnap, snap): snap for snap in snaps_list}
    for future in concurrent.futures.as_completed(future_to_replicate):
        snap = future_to_replicate[future]
        try:
            data = future.result()
        except Exception as exc:
            print(f"{snap['SnapshotId']} generated an exception: {type(exc)} {exc}")

