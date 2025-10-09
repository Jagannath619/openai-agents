"""AWS MCP Server - With Debug Logging."""

import asyncio
import json
import logging
import sys
from typing import Any

# Print to stderr for debugging
print("Starting AWS MCP Server imports...", file=sys.stderr)

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
    print("MCP imports successful", file=sys.stderr)
except Exception as e:
    print(f"Error importing MCP: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from aws_mcp_python_s3_service import S3Service
    print("S3Service imported", file=sys.stderr)
except Exception as e:
    print(f"Error importing S3Service: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from aws_mcp_python_dynamodb_service import DynamoDBService
    print("DynamoDBService imported", file=sys.stderr)
except Exception as e:
    print(f"Error importing DynamoDBService: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from aws_mcp_python_s3_tools import S3_TOOLS
    print("S3_TOOLS imported", file=sys.stderr)
except Exception as e:
    print(f"Error importing S3_TOOLS: {e}", file=sys.stderr)
    sys.exit(1)

try:
    from aws_mcp_python_dynamodb_tools import DYNAMODB_TOOLS
    print("DYNAMODB_TOOLS imported", file=sys.stderr)
except Exception as e:
    print(f"Error importing DYNAMODB_TOOLS: {e}", file=sys.stderr)
    sys.exit(1)

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

print("Initializing services...", file=sys.stderr)

# Initialize services
try:
    s3_service = S3Service()
    print("S3Service initialized", file=sys.stderr)
except Exception as e:
    print(f"Error initializing S3Service: {e}", file=sys.stderr)
    sys.exit(1)

try:
    dynamodb_service = DynamoDBService()
    print("DynamoDBService initialized", file=sys.stderr)
except Exception as e:
    print(f"Error initializing DynamoDBService: {e}", file=sys.stderr)
    sys.exit(1)

# Create server instance
print("Creating MCP server...", file=sys.stderr)
app = Server("aws-mcp-server")
print("MCP server created", file=sys.stderr)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    print("list_tools called", file=sys.stderr)
    return S3_TOOLS + DYNAMODB_TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    print(f"call_tool called: {name}", file=sys.stderr)
    try:
        result = None
        
        # S3 Operations
        if name == "s3_bucket_create":
            result = s3_service.create_bucket(
                arguments["bucketName"],
                arguments.get("region")
            )
        elif name == "s3_bucket_list":
            result = s3_service.list_buckets()
        elif name == "s3_bucket_delete":
            result = s3_service.delete_bucket(arguments["bucketName"])
        elif name == "s3_object_upload":
            result = s3_service.upload_object(
                arguments["bucketName"],
                arguments["key"],
                arguments["content"],
                arguments.get("contentType", "text/plain")
            )
        elif name == "s3_object_delete":
            result = s3_service.delete_object(
                arguments["bucketName"],
                arguments["key"]
            )
        elif name == "s3_object_list":
            result = s3_service.list_objects(
                arguments["bucketName"],
                arguments.get("prefix"),
                arguments.get("maxKeys", 1000)
            )
        elif name == "s3_object_read":
            result = s3_service.read_object(
                arguments["bucketName"],
                arguments["key"]
            )
        
        # DynamoDB Table Operations
        elif name == "dynamodb_table_create":
            result = dynamodb_service.create_table(
                arguments["tableName"],
                arguments["keySchema"],
                arguments["attributeDefinitions"],
                arguments.get("billingMode", "PAY_PER_REQUEST"),
                arguments.get("provisionedThroughput")
            )
        elif name == "dynamodb_table_describe":
            result = dynamodb_service.describe_table(arguments["tableName"])
        elif name == "dynamodb_table_delete":
            result = dynamodb_service.delete_table(arguments["tableName"])
        elif name == "dynamodb_table_update":
            result = dynamodb_service.update_table(
                arguments["tableName"],
                arguments.get("billingMode"),
                arguments.get("provisionedThroughput")
            )
        
        # DynamoDB Item Operations
        elif name == "dynamodb_item_put":
            result = dynamodb_service.put_item(
                arguments["tableName"],
                arguments["item"]
            )
        elif name == "dynamodb_item_get":
            result = dynamodb_service.get_item(
                arguments["tableName"],
                arguments["key"]
            )
        elif name == "dynamodb_item_update":
            result = dynamodb_service.update_item(
                arguments["tableName"],
                arguments["key"],
                arguments["updateExpression"],
                arguments.get("expressionAttributeNames"),
                arguments.get("expressionAttributeValues")
            )
        elif name == "dynamodb_item_delete":
            result = dynamodb_service.delete_item(
                arguments["tableName"],
                arguments["key"]
            )
        elif name == "dynamodb_item_query":
            result = dynamodb_service.query_items(
                arguments["tableName"],
                arguments["keyConditionExpression"],
                arguments.get("expressionAttributeNames"),
                arguments.get("expressionAttributeValues"),
                arguments.get("filterExpression"),
                arguments.get("limit"),
                arguments.get("indexName")
            )
        elif name == "dynamodb_item_scan":
            result = dynamodb_service.scan_items(
                arguments["tableName"],
                arguments.get("filterExpression"),
                arguments.get("expressionAttributeNames"),
                arguments.get("expressionAttributeValues"),
                arguments.get("limit")
            )
        
        # DynamoDB Batch Operations
        elif name == "dynamodb_batch_get":
            result = dynamodb_service.batch_get_items(arguments["requestItems"])
        elif name == "dynamodb_item_batch_write":
            result = dynamodb_service.batch_write_items(arguments["requestItems"])
        elif name == "dynamodb_batch_execute":
            result = dynamodb_service.batch_execute_statements(arguments["statements"])
        
        # DynamoDB TTL Operations
        elif name == "dynamodb_describe_ttl":
            result = dynamodb_service.describe_ttl(arguments["tableName"])
        elif name == "dynamodb_update_ttl":
            result = dynamodb_service.update_ttl(
                arguments["tableName"],
                arguments["enabled"],
                arguments["attributeName"]
            )
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        print(f"Error in call_tool: {e}", file=sys.stderr)
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main() -> None:
    """Main entry point for the server."""
    print("Starting main() function...", file=sys.stderr)
    logger.info("Starting AWS MCP Server...")
    
    try:
        print("Creating stdio_server...", file=sys.stderr)
        async with stdio_server() as (read_stream, write_stream):
            print("stdio_server created, running app...", file=sys.stderr)
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        print(f"Error in main: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    print("__main__ block executing...", file=sys.stderr)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)