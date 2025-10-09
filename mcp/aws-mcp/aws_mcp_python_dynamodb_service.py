"""DynamoDB service implementation."""

from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import ClientError
from aws_mcp_python_config import aws_config


class DynamoDBService:
    """Service for DynamoDB operations."""

    def __init__(self) -> None:
        self.client = boto3.client("dynamodb", **aws_config.get_boto3_config())
        self.resource = boto3.resource("dynamodb", **aws_config.get_boto3_config())

    # Table Operations
    def create_table(
        self,
        table_name: str,
        key_schema: List[Dict[str, str]],
        attribute_definitions: List[Dict[str, str]],
        billing_mode: str = "PAY_PER_REQUEST",
        provisioned_throughput: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """Create a new DynamoDB table."""
        try:
            params = {
                "TableName": table_name,
                "KeySchema": [
                    {"AttributeName": k["attributeName"], "KeyType": k["keyType"]}
                    for k in key_schema
                ],
                "AttributeDefinitions": [
                    {
                        "AttributeName": a["attributeName"],
                        "AttributeType": a["attributeType"],
                    }
                    for a in attribute_definitions
                ],
                "BillingMode": billing_mode,
            }

            if billing_mode == "PROVISIONED" and provisioned_throughput:
                params["ProvisionedThroughput"] = {
                    "ReadCapacityUnits": provisioned_throughput["readCapacityUnits"],
                    "WriteCapacityUnits": provisioned_throughput["writeCapacityUnits"],
                }

            response = self.client.create_table(**params)
            
            return {
                "success": True,
                "tableName": table_name,
                "tableArn": response["TableDescription"].get("TableArn"),
                "tableStatus": response["TableDescription"].get("TableStatus"),
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """Get details about a DynamoDB table."""
        try:
            response = self.client.describe_table(TableName=table_name)
            table = response["Table"]
            
            return {
                "table": {
                    "tableName": table.get("TableName"),
                    "tableStatus": table.get("TableStatus"),
                    "tableArn": table.get("TableArn"),
                    "creationDateTime": table.get("CreationDateTime").isoformat() if table.get("CreationDateTime") else None,
                    "itemCount": table.get("ItemCount"),
                    "tableSizeBytes": table.get("TableSizeBytes"),
                    "keySchema": table.get("KeySchema"),
                    "attributeDefinitions": table.get("AttributeDefinitions"),
                    "billingMode": table.get("BillingModeSummary", {}).get("BillingMode"),
                }
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def delete_table(self, table_name: str) -> Dict[str, Any]:
        """Delete a DynamoDB table."""
        try:
            response = self.client.delete_table(TableName=table_name)
            return {
                "success": True,
                "tableName": table_name,
                "tableStatus": response["TableDescription"].get("TableStatus"),
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def update_table(
        self,
        table_name: str,
        billing_mode: Optional[str] = None,
        provisioned_throughput: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """Update a DynamoDB table."""
        try:
            params = {"TableName": table_name}
            
            if billing_mode:
                params["BillingMode"] = billing_mode
            
            if billing_mode == "PROVISIONED" and provisioned_throughput:
                params["ProvisionedThroughput"] = {
                    "ReadCapacityUnits": provisioned_throughput["readCapacityUnits"],
                    "WriteCapacityUnits": provisioned_throughput["writeCapacityUnits"],
                }

            response = self.client.update_table(**params)
            return {
                "success": True,
                "tableName": table_name,
                "tableStatus": response["TableDescription"].get("TableStatus"),
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    # Item Operations
    def put_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Put an item into a DynamoDB table."""
        try:
            table = self.resource.Table(table_name)
            table.put_item(Item=item)
            return {"success": True, "tableName": table_name}
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def get_item(self, table_name: str, key: Dict[str, Any]) -> Dict[str, Any]:
        """Get an item from a DynamoDB table."""
        try:
            table = self.resource.Table(table_name)
            response = table.get_item(Key=key)
            return {"item": response.get("Item")}
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an item in a DynamoDB table."""
        try:
            table = self.resource.Table(table_name)
            params = {
                "Key": key,
                "UpdateExpression": update_expression,
                "ReturnValues": "ALL_NEW",
            }
            
            if expression_attribute_names:
                params["ExpressionAttributeNames"] = expression_attribute_names
            if expression_attribute_values:
                params["ExpressionAttributeValues"] = expression_attribute_values

            response = table.update_item(**params)
            return {"success": True, "attributes": response.get("Attributes")}
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def delete_item(self, table_name: str, key: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an item from a DynamoDB table."""
        try:
            table = self.resource.Table(table_name)
            table.delete_item(Key=key)
            return {"success": True, "tableName": table_name}
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def query_items(
        self,
        table_name: str,
        key_condition_expression: str,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        filter_expression: Optional[str] = None,
        limit: Optional[int] = None,
        index_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query items in a DynamoDB table."""
        try:
            table = self.resource.Table(table_name)
            from boto3.dynamodb.conditions import Key, Attr
            
            params = {}
            
            if expression_attribute_values:
                # Build key condition using values
                key_parts = key_condition_expression.split("=")
                if len(key_parts) == 2:
                    key_name = key_parts[0].strip()
                    value_placeholder = key_parts[1].strip()
                    if value_placeholder in expression_attribute_values:
                        params["KeyConditionExpression"] = Key(key_name).eq(
                            expression_attribute_values[value_placeholder]
                        )
            
            if expression_attribute_names:
                params["ExpressionAttributeNames"] = expression_attribute_names
            if filter_expression:
                params["FilterExpression"] = filter_expression
            if limit:
                params["Limit"] = limit
            if index_name:
                params["IndexName"] = index_name

            response = table.query(**params)
            return {
                "items": response.get("Items", []),
                "count": response.get("Count", 0),
                "scannedCount": response.get("ScannedCount", 0),
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def scan_items(
        self,
        table_name: str,
        filter_expression: Optional[str] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Scan items in a DynamoDB table."""
        try:
            table = self.resource.Table(table_name)
            params = {}
            
            if filter_expression:
                params["FilterExpression"] = filter_expression
            if expression_attribute_names:
                params["ExpressionAttributeNames"] = expression_attribute_names
            if expression_attribute_values:
                params["ExpressionAttributeValues"] = expression_attribute_values
            if limit:
                params["Limit"] = limit

            response = table.scan(**params)
            return {
                "items": response.get("Items", []),
                "count": response.get("Count", 0),
                "scannedCount": response.get("ScannedCount", 0),
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    # Batch Operations
    def batch_get_items(self, request_items: Dict[str, Any]) -> Dict[str, Any]:
        """Batch get multiple items from DynamoDB tables."""
        try:
            response = self.resource.batch_get_item(RequestItems=request_items)
            return {
                "responses": response.get("Responses", {}),
                "unprocessedKeys": response.get("UnprocessedKeys", {}),
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def batch_write_items(self, request_items: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Batch write operations (put/delete) for DynamoDB items."""
        try:
            response = self.resource.batch_write_item(RequestItems=request_items)
            return {
                "success": True,
                "unprocessedItems": response.get("UnprocessedItems", {}),
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def batch_execute_statements(self, statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple PartiQL statements in a batch."""
        try:
            response = self.client.batch_execute_statement(
                Statements=[
                    {
                        "Statement": stmt["statement"],
                        "Parameters": stmt.get("parameters", []),
                    }
                    for stmt in statements
                ]
            )
            return {"responses": response.get("Responses", [])}
        except ClientError as e:
            return {"success": False, "error": str(e)}

    # TTL Operations
    def describe_ttl(self, table_name: str) -> Dict[str, Any]:
        """Get the TTL settings for a table."""
        try:
            response = self.client.describe_time_to_live(TableName=table_name)
            ttl_desc = response.get("TimeToLiveDescription", {})
            return {
                "ttlDescription": {
                    "timeToLiveStatus": ttl_desc.get("TimeToLiveStatus"),
                    "attributeName": ttl_desc.get("AttributeName"),
                }
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}

    def update_ttl(
        self, table_name: str, enabled: bool, attribute_name: str
    ) -> Dict[str, Any]:
        """Update the TTL settings for a table."""
        try:
            response = self.client.update_time_to_live(
                TableName=table_name,
                TimeToLiveSpecification={
                    "Enabled": enabled,
                    "AttributeName": attribute_name,
                },
            )
            return {
                "success": True,
                "ttlSpecification": response.get("TimeToLiveSpecification"),
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}