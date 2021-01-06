import boto3

session = boto3.Session(profile_name="ec2_user",region_name="us-east-1")
ec2_re = session.resource(service_name="ec2")

print("Instances info with resources")
for each_in in ec2_re.instances.all():
    print(each_in.id, each_in.state['Name'])