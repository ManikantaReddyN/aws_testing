import boto3
import json
import argparse
from collections import defaultdict


def pass_Argument():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-r', action='store', type=str)
    args = my_parser.parse_args()
    if args.r:
        fetch_ec2_instance_inRegion(args.r)
    else:
        fetch_ec2_instances_and_print()


def fetch_ec2_instance_inRegion(get_region):
    ec2 = boto3.resource('ec2', region_name=get_region)
    running_instances = ec2.instances.filter(Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']}])

    ec2info = defaultdict()
    for instance in running_instances:
        for tag in instance.tags:
            if 'Name' in tag['Key']:
                name = tag['Value']
        ec2info[instance.id] = {
            'Name': name,
            'id': instance.id,
            'Type': instance.instance_type,
            'State': instance.state['Name'],
            'Private IP': instance.private_ip_address,
            'Public IP': instance.public_ip_address,
            'Launch Time': instance.launch_time
        }
    total_instances = 0
    attributes = ['Name', 'id', 'Type', 'State', 'Private IP', 'Public IP', 'Launch Time']
    for instance_id, instance in ec2info.items():
        total_instances = total_instances + 1
        for key in attributes:
            print("{0}: {1}".format(key, instance[key]))
        print("------")

    print("Total Instances : ", total_instances)


def fetch_ec2_instances_and_print():
    session = boto3.Session(profile_name="ec2_user")
    client = session.client(service_name='ec2')
    all_regions = client.describe_regions()
    regions_list = []
    for region in all_regions['Regions']:
        regions_list.append(region['RegionName'])

    json_list = []
    count = 0
    resources = session.resource(service_name="ec2")
    for region in regions_list:
        print("The instances for the region :", region)
        ec2 = boto3.resource('ec2', region_name=region)
        running_instances = ec2.instances.filter(Filters=[{
            'Name': 'instance-state-name',
            'Values': ['running']}])

        ec2info = defaultdict()
        for instance in running_instances:
            for tag in instance.tags:
                b = False
                if 'Name' in tag['Key']:
                    name = tag['Value']
                    lTime = instance.launch_time
                    lt = lTime.strftime("%m/%d/%Y, %H:%M:%S")
                    ec2info[count] = {
                        'Name': name,
                        'id': instance.id,
                        'Type': instance.instance_type,
                        'State': instance.state['Name'],
                        'Private IP': instance.private_ip_address,
                        'Public IP': instance.public_ip_address,
                        'Launch Time': lt
                    }
                    count = count + 1
        json_list.append(ec2info)

        total_insatnces = 0
        attributes = ['Name', 'id', 'Type', 'State', 'Private IP', 'Public IP', 'Launch Time']
        for instance_id, instance in ec2info.items():

            total_insatnces = total_insatnces + 1
            for key in attributes:
                print("{0}: {1}".format(key, instance[key]))
            print("-------------------------")

        print("Total Instances : ", total_insatnces)

    print("Total instances in all regions :", count)
    with open('instances18.json', 'a') as json_file:
        json.dump(json_list, json_file, indent=3)


if __name__ == '__main__':
    pass_Argument()
