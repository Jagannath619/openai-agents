"""EC2 tool definitions for the MCP server."""

from __future__ import annotations

from mcp.types import Tool

EC2_TOOLS = [
    Tool(
        name="ec2_describe_instances",
        description="Describe EC2 instances with optional filters or instance IDs.",
        inputSchema={
            "type": "object",
            "properties": {
                "instanceIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of EC2 instance IDs to describe.",
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
                    "description": "Filters to apply to the describe_instances call.",
                },
            },
        },
    ),
    Tool(
        name="ec2_start_instances",
        description="Start one or more stopped EC2 instances.",
        inputSchema={
            "type": "object",
            "properties": {
                "instanceIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of instances to start.",
                }
            },
            "required": ["instanceIds"],
        },
    ),
    Tool(
        name="ec2_stop_instances",
        description="Stop one or more running EC2 instances.",
        inputSchema={
            "type": "object",
            "properties": {
                "instanceIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of instances to stop.",
                },
                "force": {
                    "type": "boolean",
                    "description": "Force stop the instances (may cause data loss).",
                },
            },
            "required": ["instanceIds"],
        },
    ),
    Tool(
        name="ec2_reboot_instances",
        description="Reboot one or more EC2 instances.",
        inputSchema={
            "type": "object",
            "properties": {
                "instanceIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of instances to reboot.",
                }
            },
            "required": ["instanceIds"],
        },
    ),
    Tool(
        name="ec2_terminate_instances",
        description="Terminate one or more EC2 instances.",
        inputSchema={
            "type": "object",
            "properties": {
                "instanceIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of instances to terminate.",
                }
            },
            "required": ["instanceIds"],
        },
    ),
    Tool(
        name="ec2_get_instance_status",
        description="Retrieve EC2 instance status checks and health information.",
        inputSchema={
            "type": "object",
            "properties": {
                "instanceIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of instances to inspect.",
                },
                "includeAllInstances": {
                    "type": "boolean",
                    "description": "If true, include all instances regardless of status checks.",
                },
            },
        },
    ),
    Tool(
        name="ec2_run_command",
        description="Run a shell command on EC2 instances using AWS Systems Manager.",
        inputSchema={
            "type": "object",
            "properties": {
                "instanceIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of instances where the command will be executed.",
                },
                "command": {
                    "type": "string",
                    "description": "Shell command to execute.",
                },
                "documentName": {
                    "type": "string",
                    "description": "Optional SSM document name. Defaults to AWS-RunShellScript.",
                },
                "comment": {
                    "type": "string",
                    "description": "Comment to associate with the command execution.",
                },
                "executionTimeout": {
                    "type": "integer",
                    "description": "Timeout in seconds for the command execution.",
                },
                "waitForCompletion": {
                    "type": "boolean",
                    "description": "Whether to wait for the command to finish and return output.",
                },
                "pollInterval": {
                    "type": "number",
                    "description": "Polling interval in seconds when waiting for command completion.",
                },
            },
            "required": ["instanceIds", "command"],
        },
    ),
    Tool(
        name="ec2_get_instance_metrics",
        description="Fetch recent CPU and memory utilization metrics for an EC2 instance.",
        inputSchema={
            "type": "object",
            "properties": {
                "instanceId": {
                    "type": "string",
                    "description": "ID of the instance to query.",
                },
                "period": {
                    "type": "integer",
                    "description": "Granularity of the datapoints in seconds (default 300).",
                },
                "lookbackMinutes": {
                    "type": "integer",
                    "description": "Time window in minutes to query metrics (default 10).",
                },
            },
            "required": ["instanceId"],
        },
    ),
]
