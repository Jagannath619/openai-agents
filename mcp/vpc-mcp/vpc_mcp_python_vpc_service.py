"""VPC service implementation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from vpc_mcp_python_config import aws_config


class VPCService:
    """Service layer for interacting with AWS VPC resources."""

    def __init__(self) -> None:
        self.client = boto3.client("ec2", **aws_config.get_boto3_config())

    def create_vpc(
        self,
        cidr_block: str,
        instance_tenancy: str | None = None,
        amazon_provided_ipv6: bool | None = None,
    ) -> Dict[str, Any]:
        """Create a new VPC."""
        try:
            params: Dict[str, Any] = {"CidrBlock": cidr_block}
            if instance_tenancy:
                params["InstanceTenancy"] = instance_tenancy
            if amazon_provided_ipv6 is not None:
                params["AmazonProvidedIpv6CidrBlock"] = amazon_provided_ipv6

            response = self.client.create_vpc(**params)
            return {"success": True, "vpc": response.get("Vpc", {})}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def delete_vpc(self, vpc_id: str) -> Dict[str, Any]:
        """Delete a VPC."""
        try:
            self.client.delete_vpc(VpcId=vpc_id)
            return {"success": True, "vpcId": vpc_id}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def describe_vpcs(
        self,
        vpc_ids: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Describe VPCs."""
        try:
            params: Dict[str, Any] = {}
            if vpc_ids:
                params["VpcIds"] = vpc_ids
            if filters:
                params["Filters"] = filters

            response = self.client.describe_vpcs(**params)
            return {"success": True, "vpcs": response.get("Vpcs", [])}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def create_subnet(
        self,
        vpc_id: str,
        cidr_block: str,
        availability_zone: Optional[str] = None,
        ipv6_cidr_block: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a subnet in a VPC."""
        try:
            params: Dict[str, Any] = {
                "VpcId": vpc_id,
                "CidrBlock": cidr_block,
            }
            if availability_zone:
                params["AvailabilityZone"] = availability_zone
            if ipv6_cidr_block:
                params["Ipv6CidrBlock"] = ipv6_cidr_block

            response = self.client.create_subnet(**params)
            return {"success": True, "subnet": response.get("Subnet", {})}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def delete_subnet(self, subnet_id: str) -> Dict[str, Any]:
        """Delete a subnet."""
        try:
            self.client.delete_subnet(SubnetId=subnet_id)
            return {"success": True, "subnetId": subnet_id}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def describe_subnets(
        self,
        subnet_ids: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Describe subnets."""
        try:
            params: Dict[str, Any] = {}
            if subnet_ids:
                params["SubnetIds"] = subnet_ids
            if filters:
                params["Filters"] = filters

            response = self.client.describe_subnets(**params)
            return {"success": True, "subnets": response.get("Subnets", [])}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def create_internet_gateway(self) -> Dict[str, Any]:
        """Create an internet gateway."""
        try:
            response = self.client.create_internet_gateway()
            return {"success": True, "internetGateway": response.get("InternetGateway", {})}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def delete_internet_gateway(self, internet_gateway_id: str) -> Dict[str, Any]:
        """Delete an internet gateway."""
        try:
            self.client.delete_internet_gateway(InternetGatewayId=internet_gateway_id)
            return {"success": True, "internetGatewayId": internet_gateway_id}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def attach_internet_gateway(self, internet_gateway_id: str, vpc_id: str) -> Dict[str, Any]:
        """Attach an internet gateway to a VPC."""
        try:
            self.client.attach_internet_gateway(
                InternetGatewayId=internet_gateway_id,
                VpcId=vpc_id,
            )
            return {"success": True, "internetGatewayId": internet_gateway_id, "vpcId": vpc_id}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def detach_internet_gateway(self, internet_gateway_id: str, vpc_id: str) -> Dict[str, Any]:
        """Detach an internet gateway from a VPC."""
        try:
            self.client.detach_internet_gateway(
                InternetGatewayId=internet_gateway_id,
                VpcId=vpc_id,
            )
            return {"success": True, "internetGatewayId": internet_gateway_id, "vpcId": vpc_id}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def create_route_table(self, vpc_id: str) -> Dict[str, Any]:
        """Create a route table."""
        try:
            response = self.client.create_route_table(VpcId=vpc_id)
            return {"success": True, "routeTable": response.get("RouteTable", {})}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def delete_route_table(self, route_table_id: str) -> Dict[str, Any]:
        """Delete a route table."""
        try:
            self.client.delete_route_table(RouteTableId=route_table_id)
            return {"success": True, "routeTableId": route_table_id}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def associate_route_table(self, route_table_id: str, subnet_id: str) -> Dict[str, Any]:
        """Associate a route table with a subnet."""
        try:
            response = self.client.associate_route_table(
                RouteTableId=route_table_id,
                SubnetId=subnet_id,
            )
            return {
                "success": True,
                "associationId": response.get("AssociationId"),
                "routeTableId": route_table_id,
                "subnetId": subnet_id,
            }
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def disassociate_route_table(self, association_id: str) -> Dict[str, Any]:
        """Disassociate a route table from a subnet."""
        try:
            self.client.disassociate_route_table(AssociationId=association_id)
            return {"success": True, "associationId": association_id}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def create_security_group(
        self,
        group_name: str,
        description: str,
        vpc_id: str,
    ) -> Dict[str, Any]:
        """Create a security group."""
        try:
            response = self.client.create_security_group(
                GroupName=group_name,
                Description=description,
                VpcId=vpc_id,
            )
            return {"success": True, "groupId": response.get("GroupId")}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def delete_security_group(self, group_id: str) -> Dict[str, Any]:
        """Delete a security group."""
        try:
            self.client.delete_security_group(GroupId=group_id)
            return {"success": True, "groupId": group_id}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def describe_security_groups(
        self,
        group_ids: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Describe security groups."""
        try:
            params: Dict[str, Any] = {}
            if group_ids:
                params["GroupIds"] = group_ids
            if filters:
                params["Filters"] = filters

            response = self.client.describe_security_groups(**params)
            return {"success": True, "securityGroups": response.get("SecurityGroups", [])}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def authorize_security_group_ingress(
        self,
        group_id: str,
        ip_permissions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Authorize security group ingress rules."""
        try:
            self.client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions,
            )
            return {"success": True, "groupId": group_id, "ipPermissions": ip_permissions}
        except ClientError as error:
            return {"success": False, "error": str(error)}

    def revoke_security_group_ingress(
        self,
        group_id: str,
        ip_permissions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Revoke security group ingress rules."""
        try:
            self.client.revoke_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions,
            )
            return {"success": True, "groupId": group_id, "ipPermissions": ip_permissions}
        except ClientError as error:
            return {"success": False, "error": str(error)}
