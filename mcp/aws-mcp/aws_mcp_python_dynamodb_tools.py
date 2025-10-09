"""DynamoDB tool definitions."""

from mcp.types import Tool

# DynamoDB Tool Definitions
DYNAMODB_TOOLS = [
    # Table Operations
    Tool(
        name="dynamodb_table_create",
        description="Create a new DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table to create"},
                "keySchema": {
                    "type": "array",
                    "description": "Key schema defining the primary key",
                    "items": {
                        "type": "object",
                        "properties": {
                            "attributeName": {"type": "string"},
                            "keyType": {"type": "string", "enum": ["HASH", "RANGE"]},
                        },
                        "required": ["attributeName", "keyType"],
                    },
                },
                "attributeDefinitions": {
                    "type": "array",
                    "description": "Attribute definitions for key attributes",
                    "items": {
                        "type": "object",
                        "properties": {
                            "attributeName": {"type": "string"},
                            "attributeType": {"type": "string", "enum": ["S", "N", "B"]},
                        },
                        "required": ["attributeName", "attributeType"],
                    },
                },
                "billingMode": {
                    "type": "string",
                    "enum": ["PROVISIONED", "PAY_PER_REQUEST"],
                    "description": "Billing mode (default: PAY_PER_REQUEST)",
                },
                "provisionedThroughput": {
                    "type": "object",
                    "properties": {
                        "readCapacityUnits": {"type": "number"},
                        "writeCapacityUnits": {"type": "number"},
                    },
                    "description": "Required if billingMode is PROVISIONED",
                },
            },
            "required": ["tableName", "keySchema", "attributeDefinitions"],
        },
    ),
    Tool(
        name="dynamodb_table_describe",
        description="Get details about a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
            },
            "required": ["tableName"],
        },
    ),
    Tool(
        name="dynamodb_table_delete",
        description="Delete a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table to delete"},
            },
            "required": ["tableName"],
        },
    ),
    Tool(
        name="dynamodb_table_update",
        description="Update a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
                "billingMode": {
                    "type": "string",
                    "enum": ["PROVISIONED", "PAY_PER_REQUEST"],
                    "description": "Billing mode",
                },
                "provisionedThroughput": {
                    "type": "object",
                    "properties": {
                        "readCapacityUnits": {"type": "number"},
                        "writeCapacityUnits": {"type": "number"},
                    },
                },
            },
            "required": ["tableName"],
        },
    ),
    # Item Operations
    Tool(
        name="dynamodb_item_put",
        description="Put an item into a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
                "item": {
                    "type": "object",
                    "description": "Item to put (JSON object)",
                },
            },
            "required": ["tableName", "item"],
        },
    ),
    Tool(
        name="dynamodb_item_get",
        description="Get an item from a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
                "key": {
                    "type": "object",
                    "description": "Primary key of the item",
                },
            },
            "required": ["tableName", "key"],
        },
    ),
    Tool(
        name="dynamodb_item_update",
        description="Update an item in a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
                "key": {"type": "object", "description": "Primary key of the item"},
                "updateExpression": {
                    "type": "string",
                    "description": "Update expression (e.g., 'SET #name = :name')",
                },
                "expressionAttributeNames": {
                    "type": "object",
                    "description": "Mapping of expression attribute names",
                },
                "expressionAttributeValues": {
                    "type": "object",
                    "description": "Mapping of expression attribute values",
                },
            },
            "required": ["tableName", "key", "updateExpression"],
        },
    ),
    Tool(
        name="dynamodb_item_delete",
        description="Delete an item from a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
                "key": {"type": "object", "description": "Primary key of the item"},
            },
            "required": ["tableName", "key"],
        },
    ),
    Tool(
        name="dynamodb_item_query",
        description="Query items in a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
                "keyConditionExpression": {
                    "type": "string",
                    "description": "Key condition expression",
                },
                "expressionAttributeNames": {
                    "type": "object",
                    "description": "Mapping of expression attribute names",
                },
                "expressionAttributeValues": {
                    "type": "object",
                    "description": "Mapping of expression attribute values",
                },
                "filterExpression": {
                    "type": "string",
                    "description": "Filter expression (optional)",
                },
                "limit": {"type": "number", "description": "Maximum items to return"},
                "indexName": {"type": "string", "description": "Index name for query"},
            },
            "required": ["tableName", "keyConditionExpression"],
        },
    ),
    Tool(
        name="dynamodb_item_scan",
        description="Scan items in a DynamoDB table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
                "filterExpression": {"type": "string", "description": "Filter expression"},
                "expressionAttributeNames": {
                    "type": "object",
                    "description": "Mapping of expression attribute names",
                },
                "expressionAttributeValues": {
                    "type": "object",
                    "description": "Mapping of expression attribute values",
                },
                "limit": {"type": "number", "description": "Maximum items to return"},
            },
            "required": ["tableName"],
        },
    ),
    # Batch Operations
    Tool(
        name="dynamodb_batch_get",
        description="Batch get multiple items from DynamoDB tables",
        inputSchema={
            "type": "object",
            "properties": {
                "requestItems": {
                    "type": "object",
                    "description": "Request items per table",
                },
            },
            "required": ["requestItems"],
        },
    ),
    Tool(
        name="dynamodb_item_batch_write",
        description="Batch write operations (put/delete) for DynamoDB items",
        inputSchema={
            "type": "object",
            "properties": {
                "requestItems": {
                    "type": "object",
                    "description": "Write requests per table",
                },
            },
            "required": ["requestItems"],
        },
    ),
    Tool(
        name="dynamodb_batch_execute",
        description="Execute multiple PartiQL statements in a batch",
        inputSchema={
            "type": "object",
            "properties": {
                "statements": {
                    "type": "array",
                    "description": "Array of PartiQL statements",
                    "items": {
                        "type": "object",
                        "properties": {
                            "statement": {"type": "string"},
                            "parameters": {"type": "array"},
                        },
                        "required": ["statement"],
                    },
                },
            },
            "required": ["statements"],
        },
    ),
    # TTL Operations
    Tool(
        name="dynamodb_describe_ttl",
        description="Get the TTL settings for a table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
            },
            "required": ["tableName"],
        },
    ),
    Tool(
        name="dynamodb_update_ttl",
        description="Update the TTL settings for a table",
        inputSchema={
            "type": "object",
            "properties": {
                "tableName": {"type": "string", "description": "Name of the table"},
                "enabled": {"type": "boolean", "description": "Enable or disable TTL"},
                "attributeName": {
                    "type": "string",
                    "description": "Attribute name for TTL",
                },
            },
            "required": ["tableName", "enabled", "attributeName"],
        },
    ),
]
