import boto3
import pprint
import re


pp = pprint.PrettyPrinter(indent=4)
client = boto3.client('ec2')
vpcs = client.describe_vpcs()
route_table = client.describe_route_tables()
route_table =  route_table['RouteTables']



peerings_list  = client.describe_vpc_peering_connections()
peerings = {}


ec2list = client.describe_instances()
ec2_instnaces = []
#pp.pprint(ec2list)
for reserv in ec2list['Reservations']:
    for inst in  reserv['Instances']:
        ec2_instnaces.append(inst)




def get_tag_value(tags, tag_name):
    value =''
    if 'Tags' in tags:
        for tag in tags['Tags']:
            # print(tag['Key']+tag_name)
            # print(tag['Value'])
            if tag['Key'] == tag_name:
                value=tag['Value']
    return value

def get_ec2_list_in_subnet(subnet_id):
    ec2_list_local = []
    for inst in ec2_instnaces:
        for interf in inst['NetworkInterfaces']:
            if interf['SubnetId'] == subnet_id:
                ec2_list_local.append(inst)
    return ec2_list_local

for peer in peerings_list['VpcPeeringConnections']:
    peer_tmp = {}
    peer_tmp['name']=get_tag_value(peer,'Name')
    peer_tmp['acc_vpc'] = peer['AccepterVpcInfo']['OwnerId'] +'/'+peer['AccepterVpcInfo']['Region'] +'/'+peer['AccepterVpcInfo']['VpcId'] +'/'+peer_tmp['name']
    peer_tmp['acc_vpc_id'] = peer['AccepterVpcInfo']['VpcId']
    peer_tmp['req_vpc'] = peer['RequesterVpcInfo']['OwnerId'] +'/'+peer['RequesterVpcInfo']['Region'] +'/'+peer['RequesterVpcInfo']['VpcId'] +'/'+peer_tmp['name']
    peer_tmp['req_vpc_id'] = peer['RequesterVpcInfo']['VpcId']
    peerings[peer['VpcPeeringConnectionId']]=peer_tmp





def get_remote_peering_vpc(peering_id,local_vpc):
    if peerings[peering_id]['acc_vpc_id'] == local_vpc:
        return peerings[peering_id]['req_vpc']
    else:
        return peerings[peering_id]['acc_vpc']




def get_route_table(subnet):
    used_route = {}
    used_route['RouteTableId']='Lack'
    used_route['Peerings']=[]
    used_route['NatGatewayId']=[]
    used_route['NatGateway']='Lack'
    used_route['IsPublic']='False'
    used_route['GatewayId']=[]
    for route in route_table:
        for assoc in route['Associations']:
            if 'SubnetId' in assoc:
                if assoc['SubnetId']==subnet:
                    used_route['RouteTableId']=route['RouteTableId']
                    used_route['Routes']=route['Routes']
                    for rules in route['Routes']:
                        if 'VpcPeeringConnectionId' in rules:
                            used_route['Peerings'].append(rules['VpcPeeringConnectionId'])
                        elif 'NatGatewayId' in rules:
                            used_route['NatGatewayId'].append(rules['NatGatewayId'])
                            used_route['NatGateway']='Attached'
                        elif 'GatewayId' in rules:
                            used_route['GatewayId'].append(rules['GatewayId'])
                            if re.match('igw-.*', rules['GatewayId']):
                                #print('Internet Gateway'+rules['GatewayId'])
                                used_route['IsPublic']='True'
                        else:
                            pp.pprint(rules)
                    used_route['Peerings'] = list(dict.fromkeys(used_route['Peerings']))
                    return used_route
    return used_route



#print headres
print('VPC,vpc_id,CidrBlock,IsDefault,Name')
print('Subnet,vpc_id,SubnetId,AvailabilityZone,CidrBlock,AvailableIpAddressCount,Name,IsPublic,NatGateway,RouteTableId,Peerings')
print('Ec2,vpc_id,SubnetId,Name')

for vpc in vpcs['Vpcs']:
    print(
    'VPC,'+
    vpc['VpcId']+','+
    vpc['CidrBlock']+','+
    str(vpc['IsDefault'])+','+
    get_tag_value(vpc,"Name")
    )
    subnets = client.describe_subnets(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    vpc['VpcId']
                ]
            },
        ]
    )

    for subnet in subnets['Subnets']:
        subnet_route = get_route_table(subnet['SubnetId'])
        for i in range(len(subnet_route['Peerings'])):
            subnet_route['Peerings'][i] = subnet_route['Peerings'][i] +  "("+get_remote_peering_vpc(subnet_route['Peerings'][i],vpc['VpcId'])+")"

        print(
        'Subnet,'+
        vpc['VpcId']+','+
        subnet['SubnetId']+','+
        subnet['AvailabilityZone']+','+
        subnet['CidrBlock']+','+
        str(subnet['AvailableIpAddressCount'])+','+
        get_tag_value(subnet,"Name")+','+
        subnet_route['IsPublic']+','+
        subnet_route['NatGateway']+','+
        subnet_route['RouteTableId']+','+
        ' '.join(subnet_route['Peerings'])
        )


        for inst in get_ec2_list_in_subnet(subnet['SubnetId']):
            print('EC2,'+vpc['VpcId']+','+subnet['SubnetId']+','+ get_tag_value(inst,'Name'))
