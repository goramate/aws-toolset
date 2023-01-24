#!/bin/python3
import boto3
import pprint
import re
pp = pprint.PrettyPrinter(indent=4)

client = boto3.client('elbv2')
paginator = client.get_paginator('describe_load_balancers')
for page in paginator.paginate():
    for elb in page['LoadBalancers']:
        #pp.pprint(elb['LoadBalancerName'])
        listeners = client.get_paginator('describe_listeners')
        for listener_list in listeners.paginate(LoadBalancerArn=elb['LoadBalancerArn']):
            for listener in listener_list['Listeners']:
                if listener['Protocol'] == "TLS":
                    print(elb['LoadBalancerName']
                          + "," + listener['ListenerArn']
                          + "," + listener['Protocol']
                          + "," + listener['SslPolicy']
                          )
                elif listener['Protocol'] == "HTTPS":
                    print(elb['LoadBalancerName']
                          + "," + listener['ListenerArn']
                          + "," + listener['Protocol']
                          + "," + listener['SslPolicy']
                          )
