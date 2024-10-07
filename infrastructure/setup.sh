#!/bin/bash

# Define the paths to the CloudFormation templates
NCAA_SCHOOLS_TEMPLATE="./create_ncaa_schools_table.yaml"
CONFERENCES_TEMPLATE="./create_ncaa_conferences_table.yaml"

# Create the ncaa_schools table
aws cloudformation create-stack --stack-name ncaa-schools-stack --template-body file://$NCAA_SCHOOLS_TEMPLATE

# Create the conferences table
aws cloudformation create-stack --stack-name ncaa-conferences-stack --template-body file://$CONFERENCES_TEMPLATE

echo "CloudFormation stacks for ncaa_schools and conferences tables have been created."