aws ec2 describe-instances  --query 'Reservations[].Instances[].[PrivateIpAddress,PublicIpAddress,InstanceId,InstanceType,Tags[?Key==`Name`].Value[], State.Name ]' --output text | sed '$!N;s/\n/ /'
