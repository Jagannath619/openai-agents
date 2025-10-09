# AWS MCP Server (Python)

A Model Context Protocol (MCP) server implementation in Python that provides tools for AWS S3 and DynamoDB operations.

## Features

### S3 Operations
- **s3_bucket_create**: Create a new S3 bucket
- **s3_bucket_list**: List all S3 buckets
- **s3_bucket_delete**: Delete an S3 bucket
- **s3_object_upload**: Upload an object to S3
- **s3_object_delete**: Delete an object from S3
- **s3_object_list**: List objects in an S3 bucket
- **s3_object_read**: Read an object's content from S3

### DynamoDB Operations

#### Table Operations
- **dynamodb_table_create**: Create a new DynamoDB table
- **dynamodb_table_describe**: Get details about a DynamoDB table
- **dynamodb_table_delete**: Delete a DynamoDB table
- **dynamodb_table_update**: Update a DynamoDB table

#### Item Operations
- **dynamodb_item_put**: Put an item into a DynamoDB table
- **dynamodb_item_get**: Get an item from a DynamoDB table
- **dynamodb_item_update**: Update an item in a DynamoDB table
- **dynamodb_item_delete**: Delete an item from a DynamoDB table
- **dynamodb_item_query**: Query items in a DynamoDB table
- **dynamodb_item_scan**: Scan items in a DynamoDB table

#### Batch Operations
- **dynamodb_batch_get**: Batch get multiple items from DynamoDB tables
- **dynamodb_item_batch_write**: Batch write operations (put/delete) for DynamoDB items
- **dynamodb_batch_execute**: Execute multiple PartiQL statements in a batch

#### TTL Operations
- **dynamodb_describe_ttl**: Get the TTL settings for a table
- **dynamodb_update_ttl**: Update the TTL settings for a table

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aws-mcp-server
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure AWS credentials:
```bash
cp .env.example .env
```

Edit the `.env` file with your AWS credentials:
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

## Usage

### Running the Server

```bash
python -m aws_mcp_server.server
```

Or if installed:
```bash
aws-mcp-server
```

### Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black src/
```

Type checking:
```bash
mypy src/
```

## Configuration

The server uses the following environment variables:

- `AWS_REGION`: AWS region (default: us-east-1)
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_SESSION_TOKEN`: (Optional) Session token for temporary credentials

You can also use AWS credential files (`~/.aws/credentials`) or IAM roles if running on EC2/ECS.

## Example Usage

Once the server is running, you can use it with any MCP-compatible client. Here are some example operations:

### S3 Examples

```python
# Create a bucket
{
  "tool": "s3_bucket_create",
  "arguments": {
    "bucketName": "my-new-bucket",
    "region": "us-east-1"
  }
}

# Upload an object
{
  "tool": "s3_object_upload",
  "arguments": {
    "bucketName": "my-bucket",
    "key": "path/to/file.txt",
    "content": "Hello, World!",
    "contentType": "text/plain"
  }
}

# List objects
{
  "tool": "s3_object_list",
  "arguments": {
    "bucketName": "my-bucket",
    "prefix": "path/to/"
  }
}
```

### DynamoDB Examples

```python
# Create a table
{
  "tool": "dynamodb_table_create",
  "arguments": {
    "tableName": "Users",
    "keySchema": [
      {"attributeName": "userId", "keyType": "HASH"}
    ],
    "attributeDefinitions": [
      {"attributeName": "userId", "attributeType": "S"}
    ]
  }
}

# Put an item
{
  "tool": "dynamodb_item_put",
  "arguments": {
    "tableName": "Users",
    "item": {
      "userId": "123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}

# Query items
{
  "tool": "dynamodb_item_query",
  "arguments": {
    "tableName": "Users",
    "keyConditionExpression": "userId = :userId",
    "expressionAttributeValues": {
      ":userId": "123"
    }
  }
}
```

## License

MIT License
