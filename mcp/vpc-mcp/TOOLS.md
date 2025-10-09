# VPC MCP Tools

The following MCP tools are available for working with VPC-related AWS resources:

- `vpc_create`
- `vpc_delete`
- `vpc_describe`
- `subnet_create`
- `subnet_delete`
- `subnet_describe`
- `internet_gateway_create`
- `internet_gateway_delete`
- `internet_gateway_attach`
- `internet_gateway_detach`
- `route_table_create`
- `route_table_delete`
- `route_table_associate`
- `route_table_disassociate`
- `security_group_create`
- `security_group_delete`
- `security_group_describe`
- `security_group_authorize_ingress`
- `security_group_revoke_ingress`

Each entry mirrors the corresponding boto3 EC2 operation exposed via the `Tool` definitions in `vpc_mcp_python_vpc_tools.py`.
