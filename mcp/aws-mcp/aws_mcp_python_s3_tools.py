"""S3 tool definitions."""

from typing import Any
from mcp.types import Tool

# S3 Tool Definitions
S3_TOOLS = [
    Tool(
        name="s3_bucket_create",
        description="Create a new S3 bucket",
        inputSchema={
            "type": "object",
            "properties": {
                "bucketName": {
                    "type": "string",
                    "description": "Name of the bucket to create",
                },
                "region": {
                    "type": "string",
                    "description": "AWS region for the bucket (optional)",
                },
            },
            "required": ["bucketName"],
        },
    ),
    Tool(
        name="s3_bucket_list",
        description="List all S3 buckets",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="s3_bucket_delete",
        description="Delete an S3 bucket",
        inputSchema={
            "type": "object",
            "properties": {
                "bucketName": {
                    "type": "string",
                    "description": "Name of the bucket to delete",
                },
            },
            "required": ["bucketName"],
        },
    ),
    Tool(
        name="s3_object_upload",
        description="Upload an object to S3",
        inputSchema={
            "type": "object",
            "properties": {
                "bucketName": {
                    "type": "string",
                    "description": "Name of the bucket",
                },
                "key": {
                    "type": "string",
                    "description": "Object key (path) in the bucket",
                },
                "content": {
                    "type": "string",
                    "description": "Content to upload",
                },
                "contentType": {
                    "type": "string",
                    "description": "Content type (e.g., text/plain, application/json)",
                },
            },
            "required": ["bucketName", "key", "content"],
        },
    ),
    Tool(
        name="s3_object_delete",
        description="Delete an object from S3",
        inputSchema={
            "type": "object",
            "properties": {
                "bucketName": {
                    "type": "string",
                    "description": "Name of the bucket",
                },
                "key": {
                    "type": "string",
                    "description": "Object key (path) to delete",
                },
            },
            "required": ["bucketName", "key"],
        },
    ),
    Tool(
        name="s3_object_list",
        description="List objects in an S3 bucket",
        inputSchema={
            "type": "object",
            "properties": {
                "bucketName": {
                    "type": "string",
                    "description": "Name of the bucket",
                },
                "prefix": {
                    "type": "string",
                    "description": "Prefix to filter objects",
                },
                "maxKeys": {
                    "type": "number",
                    "description": "Maximum number of objects to return",
                },
            },
            "required": ["bucketName"],
        },
    ),
    Tool(
        name="s3_object_read",
        description="Read an object's content from S3",
        inputSchema={
            "type": "object",
            "properties": {
                "bucketName": {
                    "type": "string",
                    "description": "Name of the bucket",
                },
                "key": {
                    "type": "string",
                    "description": "Object key (path) to read",
                },
            },
            "required": ["bucketName", "key"],
        },
    ),
]
