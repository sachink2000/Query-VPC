import boto3
from jinja2 import Template

# Initialize the boto3 EC2 client for a specific region
region = "us-west-2"  # Set the desired region
ec2_client = boto3.client('ec2', region_name=region)

# Function to get VPC-related resources
def get_vpc_resources(region):
    vpcs = ec2_client.describe_vpcs()['Vpcs']
    subnets = ec2_client.describe_subnets()['Subnets']
    route_tables = ec2_client.describe_route_tables()['RouteTables']
    security_groups = ec2_client.describe_security_groups()['SecurityGroups']
    network_acls = ec2_client.describe_network_acls()['NetworkAcls']

    # Collect all the VPC-related data into dictionaries
    vpc_info = []
    for vpc in vpcs:
        vpc_info.append({
            'vpc_id': vpc['VpcId'],
            'cidr_block': vpc['CidrBlock'],
            'state': vpc['State'],
            'is_default': vpc['IsDefault']
        })
    
    subnet_info = []
    for subnet in subnets:
        subnet_info.append({
            'subnet_id': subnet['SubnetId'],
            'vpc_id': subnet['VpcId'],
            'cidr_block': subnet['CidrBlock'],
            'availability_zone': subnet['AvailabilityZone']
        })
    
    route_table_info = []
    for route_table in route_tables:
        route_table_info.append({
            'route_table_id': route_table['RouteTableId'],
            'vpc_id': route_table['VpcId'],
            'routes': route_table['Routes']
        })
    
    security_group_info = []
    for sg in security_groups:
        security_group_info.append({
            'sg_id': sg['GroupId'],
            'vpc_id': sg['VpcId'],
            'group_name': sg['GroupName'],
            'description': sg['Description']
        })
    
    network_acl_info = []
    for acl in network_acls:
        # Safely get the 'Default' key by using `.get()` to avoid KeyError
        default_acl = acl.get('Default', False)  # Default to False if 'Default' key is missing
        network_acl_info.append({
            'network_acl_id': acl['NetworkAclId'],
            'vpc_id': acl['VpcId'],
            'default': default_acl,
            'associations': acl['Associations']
        })
    
    return vpc_info, subnet_info, route_table_info, security_group_info, network_acl_info

# Query VPC resources for the region
vpc_info, subnet_info, route_table_info, security_group_info, network_acl_info = get_vpc_resources(region)

# HTML Template using Jinja2
html_template = """
<html>
<head>
    <title>AWS VPC Resources in {{ region }}</title>
</head>
<body>
    <h1>AWS VPC Resources in Region: {{ region }}</h1>
    
    <h2>VPCs</h2>
    <table border="1">
        <tr>
            <th>VPC ID</th>
            <th>CIDR Block</th>
            <th>State</th>
            <th>Is Default</th>
        </tr>
        {% for vpc in vpcs %}
        <tr>
            <td>{{ vpc.vpc_id }}</td>
            <td>{{ vpc.cidr_block }}</td>
            <td>{{ vpc.state }}</td>
            <td>{{ vpc.is_default }}</td>
        </tr>
        {% endfor %}
    </table>
    
    <h2>Subnets</h2>
    <table border="1">
        <tr>
            <th>Subnet ID</th>
            <th>VPC ID</th>
            <th>CIDR Block</th>
            <th>Availability Zone</th>
        </tr>
        {% for subnet in subnets %}
        <tr>
            <td>{{ subnet.subnet_id }}</td>
            <td>{{ subnet.vpc_id }}</td>
            <td>{{ subnet.cidr_block }}</td>
            <td>{{ subnet.availability_zone }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>Route Tables</h2>
    <table border="1">
        <tr>
            <th>Route Table ID</th>
            <th>VPC ID</th>
            <th>Routes</th>
        </tr>
        {% for route_table in route_tables %}
        <tr>
            <td>{{ route_table.route_table_id }}</td>
            <td>{{ route_table.vpc_id }}</td>
            <td>{{ route_table.routes|length }}</td>  <!-- Display number of routes -->
        </tr>
        {% endfor %}
    </table>

    <h2>Security Groups</h2>
    <table border="1">
        <tr>
            <th>Security Group ID</th>
            <th>VPC ID</th>
            <th>Group Name</th>
            <th>Description</th>
        </tr>
        {% for sg in security_groups %}
        <tr>
            <td>{{ sg.sg_id }}</td>
            <td>{{ sg.vpc_id }}</td>
            <td>{{ sg.group_name }}</td>
            <td>{{ sg.description }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>Network ACLs</h2>
    <table border="1">
        <tr>
            <th>Network ACL ID</th>
            <th>VPC ID</th>
            <th>Default</th>
            <th>Associations</th>
        </tr>
        {% for acl in network_acls %}
        <tr>
            <td>{{ acl.network_acl_id }}</td>
            <td>{{ acl.vpc_id }}</td>
            <td>{{ acl.default }}</td>
            <td>{{ acl.associations|length }}</td>  <!-- Display number of associations -->
        </tr>
        {% endfor %}
    </table>

</body>
</html>
"""

# Render the template with the VPC data
template = Template(html_template)
html_output = template.render(
    region=region,
    vpcs=vpc_info,
    subnets=subnet_info,
    route_tables=route_table_info,
    security_groups=security_group_info,
    network_acls=network_acl_info
)

# Save the HTML content to a file
output_filename = f"vpc_resources_in_{region}.html"
with open(output_filename, 'w') as file:
    file.write(html_output)

print(f"VPC resources report saved to {output_filename}")
