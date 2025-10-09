"""VPC tool definitions for the MCP server."""

from mcp.types import Tool

VPC_TOOLS = [
    Tool(
        name="vpc_create",
        description="Create a new VPC",
        inputSchema={
            "type": "object",
            "properties": {
                "cidrBlock": {
                    "type": "string",
                    "description": "CIDR block for the VPC (e.g., 10.0.0.0/16)",
                },
                "instanceTenancy": {
                    "type": "string",
                    "description": "Instance tenancy option (default, dedicated, host)",
                },
                "amazonProvidedIpv6": {
                    "type": "boolean",
                    "description": "Whether to request an Amazon-provided IPv6 CIDR block",
                },
            },
            "required": ["cidrBlock"],
        },
    ),
    Tool(
        name="vpc_delete",
        description="Delete a VPC",
        inputSchema={
            "type": "object",
            "properties": {
                "vpcId": {
                    "type": "string",
                    "description": "Identifier of the VPC to delete",
                }
            },
            "required": ["vpcId"],
        },
    ),
    Tool(
        name="vpc_describe",
        description="Describe one or more VPCs",
        inputSchema={
            "type": "object",
            "properties": {
                "vpcIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of VPC IDs to describe",
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Name": {"type": "string"},
                            "Values": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["Name", "Values"],
                    },
                    "description": "Filters to apply to the VPC describe call",
                },
            },
        },
    ),
    Tool(
        name="subnet_create",
        description="Create a subnet in a VPC",
        inputSchema={
            "type": "object",
            "properties": {
                "vpcId": {
                    "type": "string",
                    "description": "ID of the VPC where the subnet will be created",
                },
                "cidrBlock": {
                    "type": "string",
                    "description": "CIDR block for the subnet",
                },
                "availabilityZone": {
                    "type": "string",
                    "description": "Availability Zone for the subnet",
                },
                "ipv6CidrBlock": {
                    "type": "string",
                    "description": "Optional IPv6 CIDR block for the subnet",
                },
            },
            "required": ["vpcId", "cidrBlock"],
        },
    ),
    Tool(
        name="subnet_delete",
        description="Delete a subnet",
        inputSchema={
            "type": "object",
            "properties": {
                "subnetId": {
                    "type": "string",
                    "description": "ID of the subnet to delete",
                }
            },
            "required": ["subnetId"],
        },
    ),
    Tool(
        name="subnet_describe",
        description="Describe subnets",
        inputSchema={
            "type": "object",
            "properties": {
                "subnetIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of subnet IDs to describe",
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Name": {"type": "string"},
                            "Values": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["Name", "Values"],
                    },
                    "description": "Filters to apply to the subnet describe call",
                },
            },
        },
    ),
    Tool(
        name="internet_gateway_create",
        description="Create an internet gateway",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="internet_gateway_delete",
        description="Delete an internet gateway",
        inputSchema={
            "type": "object",
            "properties": {
                "internetGatewayId": {
                    "type": "string",
                    "description": "ID of the internet gateway to delete",
                }
            },
            "required": ["internetGatewayId"],
        },
    ),
    Tool(
        name="internet_gateway_attach",
        description="Attach an internet gateway to a VPC",
        inputSchema={
            "type": "object",
            "properties": {
                "internetGatewayId": {
                    "type": "string",
                    "description": "ID of the internet gateway",
                },
                "vpcId": {
                    "type": "string",
                    "description": "ID of the VPC",
                },
            },
            "required": ["internetGatewayId", "vpcId"],
        },
    ),
    Tool(
        name="internet_gateway_detach",
        description="Detach an internet gateway from a VPC",
        inputSchema={
            "type": "object",
            "properties": {
                "internetGatewayId": {
                    "type": "string",
                    "description": "ID of the internet gateway",
                },
                "vpcId": {
                    "type": "string",
                    "description": "ID of the VPC",
                },
            },
            "required": ["internetGatewayId", "vpcId"],
        },
    ),
    Tool(
        name="route_table_create",
        description="Create a route table",
        inputSchema={
            "type": "object",
            "properties": {
                "vpcId": {
                    "type": "string",
                    "description": "ID of the VPC",
                }
            },
            "required": ["vpcId"],
        },
    ),
    Tool(
        name="route_table_delete",
        description="Delete a route table",
        inputSchema={
            "type": "object",
            "properties": {
                "routeTableId": {
                    "type": "string",
                    "description": "ID of the route table to delete",
                }
            },
            "required": ["routeTableId"],
        },
    ),
    Tool(
        name="route_table_associate",
        description="Associate a route table with a subnet",
        inputSchema={
            "type": "object",
            "properties": {
                "routeTableId": {
                    "type": "string",
                    "description": "ID of the route table",
                },
                "subnetId": {
                    "type": "string",
                    "description": "ID of the subnet",
                },
            },
            "required": ["routeTableId", "subnetId"],
        },
    ),
    Tool(
        name="route_table_disassociate",
        description="Disassociate a route table from a subnet",
        inputSchema={
            "type": "object",
            "properties": {
                "associationId": {
                    "type": "string",
                    "description": "Association ID returned by the route table association",
                }
            },
            "required": ["associationId"],
        },
    ),
    Tool(
        name="security_group_create",
        description="Create a security group",
        inputSchema={
            "type": "object",
            "properties": {
                "groupName": {
                    "type": "string",
                    "description": "Name of the security group",
                },
                "description": {
                    "type": "string",
                    "description": "Description for the security group",
                },
                "vpcId": {
                    "type": "string",
                    "description": "VPC ID for the security group",
                },
            },
            "required": ["groupName", "description", "vpcId"],
        },
    ),
    Tool(
        name="security_group_delete",
        description="Delete a security group",
        inputSchema={
            "type": "object",
            "properties": {
                "groupId": {
                    "type": "string",
                    "description": "ID of the security group to delete",
                }
            },
            "required": ["groupId"],
        },
    ),
    Tool(
        name="security_group_describe",
        description="Describe security groups",
        inputSchema={
            "type": "object",
            "properties": {
                "groupIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of security group IDs",
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Name": {"type": "string"},
                            "Values": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["Name", "Values"],
                    },
                    "description": "Filters to apply to the security group describe call",
                },
            },
        },
    ),
    Tool(
        name="security_group_authorize_ingress",
        description="Authorize security group ingress rules",
        inputSchema={
            "type": "object",
            "properties": {
                "groupId": {
                    "type": "string",
                    "description": "Security group ID",
                },
                "ipPermissions": {
                    "type": "array",
                    "description": "List of IP permission objects as defined by AWS",
                    "items": {"type": "object"},
                },
            },
            "required": ["groupId", "ipPermissions"],
        },
    ),
    Tool(
        name="security_group_revoke_ingress",
        description="Revoke security group ingress rules",
        inputSchema={
            "type": "object",
            "properties": {
                "groupId": {
                    "type": "string",
                    "description": "Security group ID",
                },
                "ipPermissions": {
                    "type": "array",
                    "description": "List of IP permission objects to revoke",
                    "items": {"type": "object"},
                },
            },
            "required": ["groupId", "ipPermissions"],
        },
    ),
]
