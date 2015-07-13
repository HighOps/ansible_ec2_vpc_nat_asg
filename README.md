# Ansible repo for building an ec2 VPC with Auto Scaling NAT group 

*WARNING - this repo requires use of ansible v2 (devel) modules*

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

## Dependencies

- an ec2 keypair, set in the nat auto scaling launch configuration
- a pair of allocated (but not associated) EIPs
- an IAM role and policy, used by the nat instances to allocate EIPs and take over routes


## Usage

Review and create/modify a variable file, see ```vars/``` for existing examples.

Once you are happy with your var file, run it, e.g.

    ansible-playbook plays/operation/bootstrap_vpc.yml --extra-vars "env=prod"

## Issues

- the ansible modules used are currently still Pull Requests, so are subject to change and have not been approved
- the new modules require ansible v2 (devel), which is still under heavy development and subject to errors
- the route table module currently forces the destination, which means an auto scaling setup that changes it later will cause an error in a re-run 
