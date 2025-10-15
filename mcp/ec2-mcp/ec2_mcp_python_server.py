"""EC2 MCP Server implementation."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from ec2_mcp_python_ec2_service import EC2Service
from ec2_mcp_python_ec2_tools import EC2_TOOLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

ec2_service = EC2Service()
app = Server("ec2-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return EC2_TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a tool call."""
    try:
        result: Any

        if name == "ec2_describe_instances":
            result = ec2_service.describe_instances(
                instance_ids=arguments.get("instanceIds"),
                filters=arguments.get("filters"),
            )
        elif name == "ec2_start_instances":
            result = ec2_service.start_instances(arguments["instanceIds"])
        elif name == "ec2_stop_instances":
            result = ec2_service.stop_instances(
                arguments["instanceIds"],
                force=arguments.get("force", False),
            )
        elif name == "ec2_reboot_instances":
            result = ec2_service.reboot_instances(arguments["instanceIds"])
        elif name == "ec2_terminate_instances":
            result = ec2_service.terminate_instances(arguments["instanceIds"])
        elif name == "ec2_get_instance_status":
            result = ec2_service.get_instance_status(
                instance_ids=arguments.get("instanceIds"),
                include_all_instances=arguments.get("includeAllInstances", False),
            )
        elif name == "ec2_run_command":
            result = ec2_service.run_command(
                instance_ids=arguments["instanceIds"],
                command=arguments["command"],
                document_name=arguments.get("documentName", "AWS-RunShellScript"),
                comment=arguments.get("comment"),
                execution_timeout=arguments.get("executionTimeout", 600),
                wait_for_completion=arguments.get("waitForCompletion", True),
                poll_interval=float(arguments.get("pollInterval", 2.0)),
            )
        elif name == "ec2_get_instance_metrics":
            result = ec2_service.get_instance_metrics(
                instance_id=arguments["instanceId"],
                period=arguments.get("period", 300),
                lookback_minutes=arguments.get("lookbackMinutes", 10),
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
    logger.info("Starting EC2 MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
