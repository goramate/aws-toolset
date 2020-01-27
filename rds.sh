#!/bin/bash
echo "DBInstanceIdentifier,DBInstanceStatus,DBInstanceClass,AllocatedStorage,Engine,EngineVersion,CACertificateIdentifier,AutoMinorVersionUpgrade"
aws rds describe-db-instances | jq '.DBInstances[]| "\(.DBInstanceIdentifier),\(.DBInstanceStatus),\(.DBInstanceClass),\(.AllocatedStorage),\(.Engine),\(.EngineVersion),\(.CACertificateIdentifier),\(.AutoMinorVersionUpgrade)" ' | sed 's/"//g'
