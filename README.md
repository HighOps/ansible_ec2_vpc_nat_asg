# Ansible repo for building an ec2 VPC with Auto Scaling NAT group 

*WARNING - this repo requires use of ansible v2 (devel) modules*

## Summary

The playbook and example var file will create a 2 tiered AWS ec2 VPC using multiple Availability Zones (AZs). In order for the private instances to access the internet, it uses NAT instances and manages these through an auto scaling group.   

![Image of VPC](https://github.com/halberom/ansible_ec2_vpc_nat_asg/blob/master/images/VPC.png)

When the NAT instances start, they associate themselves with an EIP (so any outbound traffic comes from a known source) and, based on what subnet they're in, attempt to replace the route.  They use https://github.com/wrapp/ec2-nat-failover to do this.

## What's Included

At present, it includes
- a variable file example for setting up a multi-AZ VPC 
- an operations bootstrap playbook that loads a variable file based on the extra-var ```env``` passed, and 
    - creates the VPC
    - creates the internet gateway
    - creates the subnets
    - creates the route tables
    - creates the security groups
    - creates the nat instance auto scaling launch configuration 
    - creates the nat instance auto scaling group

## Dependencies

- you have ansible v2 (devel) installed, and the new vpc module pull requests merged in
- you have the python boto library installed
- you are using a ~/.boto config file or ENV variables for the AWS Access Key and AWS Secret Key 

## Ansible setup

Because it's using brand new VPC modules, _which are only currently available as Pull Requests (PRs)!_, the following is required

```
cd ~
mkdir git ; cd git
git clone git@github.com:ansible/ansible.git
git clone git@github.com:ansible/ansible-modules-core.git
git clone git@github.com:ansible/ansible-modules-extras.git
cd ansible-modules-core
git fetch upstream pull/1628/head:ec2_vpc_net
git checkout ec2_vpc_net

cd ansible-modules-extras
git checkout -b new_vpc_modules
git fetch upstream pull/651/head:ec2_vpc_igw
git fetch upstream pull/597/head:ec2_vpc_route_table
git fetch upstream pull/598/head:ec2_vpc_subnet
git merge ec2_vpc_igw
git merge ec2_vpc_route_table
git merge ec2_vpc_subnet
```
Then update the ansible.cfg library param to include the path to the ansible-modules-core and ansible-modules-extras directories.

## Pre-reqs

- an ec2 keypair, set in the nat auto scaling launch configuration
- a pair of allocated (but not associated) EIPs
- an IAM role and policy, used by the nat instances to allocate EIPs and take over routes, e.g.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "prodNATMonitorInstanceAccess",
            "Action": [
                "ec2:AssociateAddress",
                "ec2:CreateRoute",
                "ec2:DescribeInstances",
                "ec2:DescribeRouteTables",
                "ec2:ModifyInstanceAttribute",
                "ec2:ReplaceRoute"
            ],
            "Effect": "Allow",
            "Resource": "*",
            "Condition": {
                "ForAllValues:StringLike": {
                    "ec2:ResourceTag/Environment": "prod*",
                    "ec2:ResourceTag/Role": "nat*"
                }
            }
        }
    ]
}
```

## Usage

Review and create/modify a variable file, see ```vars/``` for existing examples.  Changes you probably want to make include
- the region
- the CIDR range and subnets
- the AMI ID for the instance type in the region
- the ssh key_name

Once you are happy with your var file, run it, e.g.

    ansible-playbook plays/operation/bootstrap_vpc.yml --extra-vars "env=prod"

## Known Issues

- the ansible modules used are currently still Pull Requests, so are subject to change and have not been approved
- the new modules require ansible v2 (devel), which is still under heavy development and subject to errors
- the route table module currently forces the destination, which means an auto scaling setup that changes it later will cause an error in a re-run 

## Todo

- create a playbook to generate an AMI with the nat_monitor script baked in
- update the nat_monitor script to create the route if it doesn't exist
- add handling of the IAM Policy
- add updating of the IAM Policy to use specific arn values for resources
