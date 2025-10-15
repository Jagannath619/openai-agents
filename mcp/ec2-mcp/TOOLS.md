# EC2 MCP Tools

This directory contains an MCP server focused on Amazon EC2 instance operations.

## Files

- `ec2_mcp_python_config.py` – Loads AWS credentials and region configuration.
- `ec2_mcp_python_ec2_service.py` – Business logic for EC2, SSM, and CloudWatch calls.
- `ec2_mcp_python_ec2_tools.py` – Tool schema definitions exposed to MCP clients.
- `ec2_mcp_python_server.py` – Stdio-based MCP server wiring tools to the service layer.
- `ec2_mcp_readme.md` – Usage instructions and feature overview.
- `requirements.txt` – Python dependencies required to run the server.
