import boto3

session = boto3.Session(profile_name="ec2_user")
client = session.client(service_name='ec2')
all_regions = client.describe_regions()
regions_list=[]
for region in all_regions['Regions']:
    print(region['RegionName'])
    regions_list.append(region['RegionName'])

print(regions_list)

for region in regions_list:
    session = boto3.Session(profile_name="ec2_user",region_name=region)
    resources= session.resource(service_name="ec2")
    print("Region name :",region)
    for every_in in resources.instances.all():
        print(every_in,every_in.state['Name'])
