#!/usr/bin/python
import boto3
import string
from pprint import pprint

client = boto3.client('ec2')
ec2_list = []
response = client.describe_instances()
#pprint(response['Reservations'][0]['Instances'])
ecstand = {'nano':0.25,'micro':0.5,'small':1,'medium':2,'large':4,'xlarge':8,'2xlarge':16,'4xlarge':32,'8xlarge':64}
ec2_usage = {}
reserv_usage = {}

def list_family(family):
    for inst in ec2_list:

        if inst['State']['Name'] == 'running':
            family_tmp= inst['InstanceType'].split(".")[0]
            size  = ecstand[inst['InstanceType'].split(".")[1]]
            if family_tmp == family:
                name ='';
                if 'Tags' in inst:
                    for tag in inst['Tags']:
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                print(name+","+inst['InstanceType'] +","+ inst['InstanceId'] + "," + str(size) + " units")


response = client.describe_instances()
for r in response:
    print(r)
for inst in response['Reservations']:
    for ins in inst['Instances']:
        ec2_list.append(ins)

print('LISTA'+str(len(ec2_list)))



for inst in ec2_list:
    if inst['State']['Name'] == 'running':
        #pprint(inst['Instances'][0]['InstanceType'])
        family = inst['InstanceType'].split(".")[0]
        if family in ec2_usage.keys():
            ec2_usage[family] = ec2_usage[family] + ecstand[inst['InstanceType'].split(".")[1]]
        else:
            ec2_usage[family] = ecstand[inst['InstanceType'].split(".")[1]]
        #print ec2_usage[family]

reservations = client.describe_reserved_instances()
for reserv in reservations['ReservedInstances']:
    if reserv['State'] == 'active':
        family = reserv['InstanceType'].split(".")[0]
        size = ecstand[reserv['InstanceType'].split(".")[1]]
        if family in reserv_usage.keys():
            reserv_usage[family] = reserv_usage[family] + (size * reserv['InstanceCount'])
        else:
            reserv_usage[family] = size * reserv['InstanceCount']
        #print reserv_usage[family]

for family in ec2_usage:
    if family in  reserv_usage:
        print( family + ": \t" + str(ec2_usage[family]) + " units "  +  str(reserv_usage[family]) + " reserved units.")
    else:
        print( family + ": \t" + str(ec2_usage[family]) + " units "  +   "0 reserved units.")
    list_family(family)

for family in reserv_usage:
    if not (family  in ec2_usage):
        print("useless reservations:" + family + " size: " + str(reserv_usage[family]) )
print("Reservations")
for reserv in reservations['ReservedInstances']:
    if reserv['State'] == 'active':
        res = reserv['InstanceType']
        print(reserv['InstanceType'] +','+ str( reserv['InstanceCount']) +','+str(reserv['End']))
