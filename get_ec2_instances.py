import boto3
import json


def fetch_ec2_instances_and_print():
    session = boto3.Session(profile_name="ec2_user")
    client = session.client(service_name='ec2')
    all_regions = client.describe_regions()
    regions_list = []
    for region in all_regions['Regions']:
        regions_list.append(region['RegionName'])

    # print(regions_list)
    json_list = []
    total_instances = 0
    for region in regions_list:
        print("The instances for the region :", region)

        session = boto3.Session(profile_name="ec2_user", region_name=region)
        resources = session.resource(service_name="ec2")
        count = 1
        for vm in resources.instances.all():
            instance_st = vm.state
            if instance_st['Name'] == "running":
                if count > 0:
                    print("Instance_id\t\t \tInstance_Type\t Launch_Time\t \tSecurity_group_name\t"
                          " Monitering_State\t Instance_Status\tPrivate_ip_Address\tPublic_ip_Address")
                    print("---------------------------------------------------------------------------------------"
                          "-----------------------------------------------------------------------------------")
                count = count - 1
                total_instances = total_instances + 1
                lTime = vm.launch_time
                lt = lTime.strftime("%m/%d/%Y, %H:%M:%S")
                private_ip = vm.private_ip_address
                public_ip = vm.public_ip_address
                monitering_state = vm.monitoring
                security_group = vm.security_groups
                details = {
                    'instance_id': vm.instance_id,
                    'instance_Type': vm.instance_type,
                    'launch_Time': lt,
                    'security_group_name': security_group[0]['GroupName'],
                    'monitering_State': monitering_state['State'],
                    'instance_Status': instance_st['Name'],
                    'private_ip_Address': private_ip,
                    'public_ip_address': public_ip
                }
                print(details['instance_id'], "|\t|", details['instance_Type'],
                      "|\t|", details['launch_Time'],
                      "|\t\t|", details['security_group_name'],
                      "|\t\t|", details['monitering_State'], "|\t\t\t|", details['instance_Status'],
                      "|\t|", details['private_ip_Address'],
                      "|\t|", details['public_ip_address'])
                json_list.append(details)
    with open('instances.json', 'a') as json_file:
        json.dump(json_list, json_file, indent=3)

    print("Total Instances in all regions :\t", total_instances)


if __name__ == '__main__':
    fetch_ec2_instances_and_print()
