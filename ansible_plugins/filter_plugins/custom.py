from jinja2.utils import soft_unicode

def get_security_groups(value, key, value, return_key='group_id'):
    # 'value' input is expected to be a results list from the ec2_group module
    # it looks for a key, e.g. 'name' and a value, e.g. 'prod_nat' and returns 
    # the return_key, e.g. 'group_id' of all that match in a list
    results = []
    for item in value:
      if key in item['item'].keys():
        if item['item'][key] == value:
          results.append(item[return_key])

    return results

def get_subnet_route_map(value, routes, key='Type', value='public'):
    # given a list of subnet results from the ec2_vpc_subnet task and a list 
    # of route results from the ec2_vpc_route_table task, return a list of 
    # dicts of public subnet_id : route_id mapping where the public subnet 
    # is in the same az as the private subnet the route is associated with
    
    # assuming all private subnets in a routing table are in the same az!

    mapping = []
    route_az_map = {}
    no_routes = {}

    # create a list of route_id:az pairs 
    for r in routes:
        for s in value:
            subnet_in_route = False
            # the route table task can take a name, cidr or id
            if 'Name' in s['subnet']['tags']:
                if s['subnet']['tags']['Name'] in r['item']['subnets']:
                    subnet_in_route = True
            elif s['subnet']['cidr'] in r['item']['subnets']:
                subnet_in_route = True
            elif s['subnet_id'] in r['item']['subnets']:
                subnet_in_route = True

            if subnet_in_route: 
                route_az_map[r['route_table_id']] = s['subnet']['az']

    # assume a distinguishing tag exists

    # get a mapping of key (public) subnets to az
    subnet_az_map = {}
    for s in value:
        if s['subnet']['tags'][key] == value:
            subnet_az_map[s['subnet_id']] = s['subnet']['az']

    # now loop through the route:az's, and find a matching public subnet based on az
    for route_table_id,route_az in route_az_map.iteritems():
        for subnet_id,subnet_az in subnet_az_map.iteritems():
            if route_az == subnet_az:
                mapping.append({'subnet_id':subnet_id, 'route_table_id':route_table_id })

    return mapping

def get_zip(value, list1):
    # return zipped result of 2 lists
    return zip(value, list1)

class FilterModule(object):
    ''' Ansible jinja2 filters '''

    def filters(self):
        return {
            'get_security_groups': get_security_groups,
            'get_subnet_route_map': get_subnet_route_map,
            'get_zip': get_zip,
        }
