import boto3
import json
import argparse
import pandas as pd
import os
from os import path


def pass_argument():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-r', action='store', type=str)
    my_parser.add_argument('-c', action='store', type=str)
    args = my_parser.parse_args()
    if args.r:
        print("You have selected instances for the region :", args.r)
        fetch_ec2_instance_in_region(args.r)
    elif args.c:
        print("Displaying any new instances launched today")
        compare()
    else:
        print("Fetching instances for all regions\n\n")
        fetch_ec2_instances_and_print(1)


def fetch_ec2_instance_in_region(get_region):
    session = boto3.Session(profile_name="ec2_user", region_name=get_region)
    resources = session.resource(service_name="ec2")
    count = 0
    json_list = []
    for vm in resources.instances.all():
        instance_st = vm.state
        if instance_st['Name'] == "running":
            count = count + 1
            time = vm.launch_time
            lt = time.strftime("%m/%d/%Y, %H:%M:%S")
            security_group = vm.security_groups
            details = {
                'Instance_id': vm.instance_id,
                'Instance_Type': vm.instance_type,
                'Launch_Time': lt,
                'Security_group_name': security_group[0]['GroupName'],
                'Instance_Status': instance_st['Name'],
                'Private_ip_Address': vm.private_ip_address,
                'Public_ip_address': vm.public_ip_address
            }
            json_list.append(details)

    print("Total instances in this region :", count)
    if count != 0:
        print_instances(json_list)


def fetch_ec2_instances_and_print(get_val):
    session = boto3.Session(profile_name="ec2_user")
    client = session.client(service_name='ec2')
    all_regions = client.describe_regions()
    regions_list = []
    for region in all_regions['Regions']:
        regions_list.append(region['RegionName'])

    json_list = []
    count = 0
    for region in regions_list:
        session = boto3.Session(profile_name="ec2_user", region_name=region)
        resources = session.resource(service_name="ec2")
        for vm in resources.instances.all():
            instance_st = vm.state
            if instance_st['Name'] == "running":
                count = count + 1
                time = vm.launch_time
                lt = time.strftime("%m/%d/%Y, %H:%M:%S")
                security_group = vm.security_groups
                details = {
                    'Region': region,
                    'Instance_id': vm.instance_id,
                    'Instance_Type': vm.instance_type,
                    'Launch_Time': lt,
                    'Security_group_name': security_group[0]['GroupName'],
                    'Instance_Status': instance_st['Name'],
                    'Private_ip_Address': vm.private_ip_address,
                    'Public_ip_address': vm.public_ip_address
                }
                json_list.append(details)
    print("Total Instances in all regions :", count)
    if get_val == 1:
        print_instances(json_list)
        with open('current_instances.json', 'a') as json_file:
            json.dump(json_list, json_file, indent=3)
        if path.exists(r'stored_instances.json'):
            os.remove(r'stored_instances.json')
        os.rename(r'current_instances.json', r'stored_instances.json')
    else:
        with open('current_instances.json', 'a') as json_file:
            json.dump(json_list, json_file, indent=3)


def print_instances(json_list):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 25)
    df = pd.DataFrame(json_list)
    print(df)


def compare():
    count = 0
    if path.exists('stored_instances.json'):
        print("Previous day file exists")
        print("Executing today's file")
        fetch_ec2_instances_and_print(0)
        with open('current_instances.json', 'r') as f1:
            instan1_dict = json.load(f1)
        with open('stored_instances.json', 'r') as f2:
            instan2_dict = json.load(f2)
        instanceid_set = set()
        for vm in instan1_dict:
            instanceid_set.add(vm['Instance_id'])

        diff_instances = []
        print("Checking for New instances")
        for vm in instan2_dict:
            if vm['Instance_id'] in instanceid_set:
                continue
            else:
                details = {
                    'Region': vm['Region'],
                    'Instance_id': vm['Instance_id'],
                    'Instance_Type': vm['Instance_Type'],
                    'Launch_Time': vm['Launch_Time'],
                    'Security_group_name': vm['Security_group_name'],
                    'Instance_Status': vm['Instance_Status'],
                    'Private_ip_Address': vm['Private_ip_Address'],
                    'Public_ip_address': vm['Public_ip_address']
                }
                count = count + 1
                diff_instances.append(details)
        print("Total number of new instances :", count)
        if count != 0:
            print_instances(diff_instances)
        os.remove(r'stored_instances.json')
        os.rename(r'current_instances.json', r'stored_instances.json')
    else:
        print("No previous day file exists\n")
        print("Exiting")


if __name__ == '__main__':
    pass_argument()
