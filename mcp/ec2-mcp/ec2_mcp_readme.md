# EC2 MCP Server

This MCP server exposes EC2 management operations as tools, allowing you to interact with instances directly from an MCP-compatible client. It complements the existing VPC MCP server by focusing on instance lifecycle, remote command execution, and operational observability (CPU and memory metrics).

## Features

- Describe EC2 instances with optional filtering
- Start, stop, reboot, and terminate instances
- Retrieve instance status checks
- Run shell commands on instances through AWS Systems Manager (SSM)
- Query recent CPU and memory utilization metrics via CloudWatch

## Prerequisites

1. Python 3.11+
2. AWS credentials with permissions for EC2, SSM, and CloudWatch
3. (Optional) [AWS CloudWatch Agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html) installed on instances to emit memory metrics
4. Systems Manager agent must be enabled for remote command execution

Export the following environment variables or create a `.env` file in the project root:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...   # optional
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the server

```bash
python ec2_mcp_python_server.py
```

The server communicates over stdio, so integrate it with your MCP-aware client by configuring the command above.

## Available tools

| Tool name | Description |
|-----------|-------------|
| `ec2_describe_instances` | Describe instances by IDs or filters |
| `ec2_start_instances` | Start stopped instances |
| `ec2_stop_instances` | Stop running instances |
| `ec2_reboot_instances` | Reboot instances |
| `ec2_terminate_instances` | Terminate instances |
| `ec2_get_instance_status` | Retrieve instance status checks |
| `ec2_run_command` | Execute shell commands via AWS Systems Manager |
| `ec2_get_instance_metrics` | Fetch CPU and memory utilization metrics |

Each tool returns structured JSON responses. `ec2_run_command` can optionally wait for the command to complete and returns invocation output when available.
