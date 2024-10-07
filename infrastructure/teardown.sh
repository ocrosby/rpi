#!/bin/bash

# Delete the ncaa_schools table stack
aws cloudformation delete-stack --stack-name ncaa-schools-stack

# Delete the conferences table stack
aws cloudformation delete-stack --stack-name ncaa-conferences-stack

echo "CloudFormation stacks for ncaa_schools and conferences tables have been deleted."