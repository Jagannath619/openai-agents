"""VPC MCP Server implementation."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from vpc_mcp_python_vpc_service import VPCService
from vpc_mcp_python_vpc_tools import VPC_TOOLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

vpc_service = VPCService()
app = Server("vpc-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return VPC_TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a tool call."""
    try:
        result: Any

        if name == "vpc_create":
            result = vpc_service.create_vpc(
                arguments["cidrBlock"],
                arguments.get("instanceTenancy"),
                arguments.get("amazonProvidedIpv6"),
            )
        elif name == "vpc_delete":
            result = vpc_service.delete_vpc(arguments["vpcId"])
        elif name == "vpc_describe":
            result = vpc_service.describe_vpcs(
                arguments.get("vpcIds"),
                arguments.get("filters"),
            )
        elif name == "subnet_create":
            result = vpc_service.create_subnet(
                arguments["vpcId"],
                arguments["cidrBlock"],
                arguments.get("availabilityZone"),
                arguments.get("ipv6CidrBlock"),
            )
        elif name == "subnet_delete":
            result = vpc_service.delete_subnet(arguments["subnetId"])
        elif name == "subnet_describe":
            result = vpc_service.describe_subnets(
                arguments.get("subnetIds"),
                arguments.get("filters"),
            )
        elif name == "internet_gateway_create":
            result = vpc_service.create_internet_gateway()
        elif name == "internet_gateway_delete":
            result = vpc_service.delete_internet_gateway(arguments["internetGatewayId"])
        elif name == "internet_gateway_attach":
            result = vpc_service.attach_internet_gateway(
                arguments["internetGatewayId"],
                arguments["vpcId"],
            )
        elif name == "internet_gateway_detach":
            result = vpc_service.detach_internet_gateway(
                arguments["internetGatewayId"],
                arguments["vpcId"],
            )
        elif name == "route_table_create":
            result = vpc_service.create_route_table(arguments["vpcId"])
        elif name == "route_table_delete":
            result = vpc_service.delete_route_table(arguments["routeTableId"])
        elif name == "route_table_associate":
            result = vpc_service.associate_route_table(
                arguments["routeTableId"],
                arguments["subnetId"],
            )
        elif name == "route_table_disassociate":
            result = vpc_service.disassociate_route_table(arguments["associationId"])
        elif name == "security_group_create":
            result = vpc_service.create_security_group(
                arguments["groupName"],
                arguments["description"],
                arguments["vpcId"],
            )
        elif name == "security_group_delete":
            result = vpc_service.delete_security_group(arguments["groupId"])
        elif name == "security_group_describe":
            result = vpc_service.describe_security_groups(
                arguments.get("groupIds"),
                arguments.get("filters"),
            )
        elif name == "security_group_authorize_ingress":
            result = vpc_service.authorize_security_group_ingress(
                arguments["groupId"],
                arguments["ipPermissions"],
            )
        elif name == "security_group_revoke_ingress":
            result = vpc_service.revoke_security_group_ingress(
                arguments["groupId"],
                arguments["ipPermissions"],
            )
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str),
            )
        ]
    except Exception as error:  # pylint: disable=broad-except
        logger.exception("Error executing tool %s", name)
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": str(error)}, indent=2),
            )
        ]


async def main() -> None:
    """Entrypoint for running the MCP server."""
    logger.info("Starting VPC MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
