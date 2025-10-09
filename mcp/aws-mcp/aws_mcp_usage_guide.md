# AWS MCP Server - Complete Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Server](#running-the-server)
4. [Connecting to Claude Desktop](#connecting-to-claude-desktop)
5. [Using the Tools](#using-the-tools)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites
- Python 3.10 or higher
- AWS Account with access credentials
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd aws-mcp-server
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Configuration

### AWS Credentials Setup

#### Option 1: Using Environment Variables (Recommended)
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

Your `.env` file should contain:
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Optional: for temporary credentials
# AWS_SESSION_TOKEN=your_session_token
```

#### Option 2: Using AWS CLI Configuration
If you have AWS CLI configured (`~/.aws/credentials`), the server will automatically use those credentials.

```bash
# Configure AWS CLI
aws configure
```

#### Option 3: Using IAM Roles (for EC2/ECS)
If running on AWS infrastructure, the server will automatically use the IAM role attached to your instance.

---

## Running the Server

### Start the Server
```bash
# Make sure your virtual environment is activated
python -m aws_mcp_server.server
```

You should see:
```
INFO:aws_mcp_server.server:Starting AWS MCP Server...
```

The server runs in stdio mode and waits for MCP client connections.

---

## Connecting to Claude Desktop

### Step 1: Locate Claude Desktop Config
The configuration file location depends on your OS:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Edit Configuration
Open the config file and add the AWS MCP server:

```json
{
  "mcpServers": {
    "aws": {
      "command": "python",
      "args": [
        "-m",
        "aws_mcp_server.server"
      ],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "your_access_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret_key"
      },
      "cwd": "/absolute/path/to/aws-mcp-server"
    }
  }
}
```

**Important Notes:**
- Replace `/absolute/path/to/aws-mcp-server` with the actual path to your project
- On Windows, use double backslashes: `C:\\Users\\YourName\\aws-mcp-server`
- Make sure Python is in your system PATH

### Step 3: Restart Claude Desktop
Close and reopen Claude Desktop to load the new configuration.

### Step 4: Verify Connection
In Claude Desktop, you should see the AWS tools available. You can ask Claude:
```
What AWS tools do you have available?
```

---

## Using the Tools

### General Syntax
When talking to Claude with the MCP server connected, you can ask it to perform AWS operations naturally:

```
Can you list all my S3 buckets?
```

```
Create a new S3 bucket called "my-data-bucket" in us-west-2
```

```
Upload this text to S3: "Hello World" to bucket "my-bucket" with key "hello.txt"
```

---

## Examples

### S3 Operations

#### Example 1: Create a Bucket
```
Create an S3 bucket called "my-new-bucket-12345" in us-east-1
```

**What Claude does:**
```json
{
  "tool": "s3_bucket_create",
  "arguments": {
    "bucketName": "my-new-bucket-12345",
    "region": "us-east-1"
  }
}
```

#### Example 2: Upload a File
```
Upload a JSON file to S3:
- Bucket: my-bucket
- Key: data/config.json
- Content: {"env": "production", "debug": false}
```

**What Claude does:**
```json
{
  "tool": "s3_object_upload",
  "arguments": {
    "bucketName": "my-bucket",
    "key": "data/config.json",
    "content": "{\"env\": \"production\", \"debug\": false}",
    "contentType": "application/json"
  }
}
```

#### Example 3: List Objects
```
Show me all objects in "my-bucket" that start with "images/"
```

**What Claude does:**
```json
{
  "tool": "s3_object_list",
  "arguments": {
    "bucketName": "my-bucket",
    "prefix": "images/"
  }
}
```

#### Example 4: Read Object Content
```
Read the content of "data/config.json" from bucket "my-bucket"
```

#### Example 5: Delete Object
```
Delete the file "old-data.txt" from bucket "my-bucket"
```

#### Example 6: Delete Bucket
```
Delete the bucket "my-old-bucket"
```

---

### DynamoDB Operations

#### Example 1: Create a Table
```
Create a DynamoDB table called "Users" with:
- Primary key: userId (string)
- Use on-demand billing
```

**What Claude does:**
```json
{
  "tool": "dynamodb_table_create",
  "arguments": {
    "tableName": "Users",
    "keySchema": [
      {"attributeName": "userId", "keyType": "HASH"}
    ],
    "attributeDefinitions": [
      {"attributeName": "userId", "attributeType": "S"}
    ],
    "billingMode": "PAY_PER_REQUEST"
  }
}
```

#### Example 2: Create Table with Sort Key
```
Create a DynamoDB table called "Orders" with:
- Partition key: customerId (string)
- Sort key: orderDate (number)
```

**What Claude does:**
```json
{
  "tool": "dynamodb_table_create",
  "arguments": {
    "tableName": "Orders",
    "keySchema": [
      {"attributeName": "customerId", "keyType": "HASH"},
      {"attributeName": "orderDate", "keyType": "RANGE"}
    ],
    "attributeDefinitions": [
      {"attributeName": "customerId", "attributeType": "S"},
      {"attributeName": "orderDate", "attributeType": "N"}
    ]
  }
}
```

#### Example 3: Put an Item
```
Add a user to the Users table:
- userId: "user123"
- name: "John Doe"
- email: "john@example.com"
- age: 30
```

**What Claude does:**
```json
{
  "tool": "dynamodb_item_put",
  "arguments": {
    "tableName": "Users",
    "item": {
      "userId": "user123",
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30
    }
  }
}
```

#### Example 4: Get an Item
```
Get the user with userId "user123" from the Users table
```

**What Claude does:**
```json
{
  "tool": "dynamodb_item_get",
  "arguments": {
    "tableName": "Users",
    "key": {
      "userId": "user123"
    }
  }
}
```

#### Example 5: Update an Item
```
Update user "user123" in the Users table:
- Set age to 31
- Set city to "New York"
```

**What Claude does:**
```json
{
  "tool": "dynamodb_item_update",
  "arguments": {
    "tableName": "Users",
    "key": {"userId": "user123"},
    "updateExpression": "SET age = :age, city = :city",
    "expressionAttributeValues": {
      ":age": 31,
      ":city": "New York"
    }
  }
}
```

#### Example 6: Query Items
```
Query all orders for customer "cust456" in the Orders table
```

**What Claude does:**
```json
{
  "tool": "dynamodb_item_query",
  "arguments": {
    "tableName": "Orders",
    "keyConditionExpression": "customerId = :customerId",
    "expressionAttributeValues": {
      ":customerId": "cust456"
    }
  }
}
```

#### Example 7: Scan with Filter
```
Scan the Users table for all users older than 25
```

**What Claude does:**
```json
{
  "tool": "dynamodb_item_scan",
  "arguments": {
    "tableName": "Users",
    "filterExpression": "age > :minAge",
    "expressionAttributeValues": {
      ":minAge": 25
    }
  }
}
```

#### Example 8: Batch Write
```
Add multiple users to the Users table in one batch:
- user456: Alice Smith, alice@example.com
- user789: Bob Jones, bob@example.com
```

**What Claude does:**
```json
{
  "tool": "dynamodb_item_batch_write",
  "arguments": {
    "requestItems": {
      "Users": [
        {
          "putRequest": {
            "item": {
              "userId": "user456",
              "name": "Alice Smith",
              "email": "alice@example.com"
            }
          }
        },
        {
          "putRequest": {
            "item": {
              "userId": "user789",
              "name": "Bob Jones",
              "email": "bob@example.com"
            }
          }
        }
      ]
    }
  }
}
```

#### Example 9: Enable TTL
```
Enable TTL on the Sessions table using the "expiresAt" attribute
```

**What Claude does:**
```json
{
  "tool": "dynamodb_update_ttl",
  "arguments": {
    "tableName": "Sessions",
    "enabled": true,
    "attributeName": "expiresAt"
  }
}
```

#### Example 10: Describe Table
```
Show me the details of the Users table
```

#### Example 11: Delete Item
```
Delete user "user123" from the Users table
```

#### Example 12: Delete Table
```
Delete the Sessions table
```

---

## Advanced Usage

### Complex Workflows

#### Example: Create Infrastructure
```
Help me set up a blog infrastructure:
1. Create an S3 bucket called "my-blog-images"
2. Create a DynamoDB table called "BlogPosts" with postId as the primary key
3. Add a sample blog post with postId "post1", title "My First Post", and content "Hello World"
```

#### Example: Data Migration
```
1. Read all items from the "OldUsers" table
2. Transform the data (add a "migrated" field set to true)
3. Write them to the "NewUsers" table using batch write
```

#### Example: Backup and Restore
```
1. Scan all items from "Products" table
2. Save them as JSON to S3 bucket "backups" with key "products-backup-2025.json"
```

---

## Troubleshooting

### Common Issues

#### 1. Server Not Starting
**Problem**: `ModuleNotFoundError: No module named 'mcp'`

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. AWS Credentials Error
**Problem**: `Unable to locate credentials`

**Solution**:
- Check your `.env` file has correct credentials
- Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set
- Test credentials with AWS CLI: `aws sts get-caller-identity`

#### 3. Permission Denied Errors
**Problem**: `AccessDenied` when performing operations

**Solution**:
- Ensure your AWS IAM user/role has necessary permissions
- For S3: `s3:CreateBucket`, `s3:PutObject`, `s3:GetObject`, etc.
- For DynamoDB: `dynamodb:CreateTable`, `dynamodb:PutItem`, `dynamodb:GetItem`, etc.

#### 4. Claude Desktop Not Detecting Server
**Problem**: Tools not appearing in Claude Desktop

**Solution**:
- Verify config file path is correct
- Check that `cwd` points to absolute path of project
- Ensure Python is in system PATH
- Restart Claude Desktop completely
- Check Claude Desktop logs for errors

#### 5. Region Errors
**Problem**: `IllegalLocationConstraintException`

**Solution**:
- For us-east-1, don't specify CreateBucketConfiguration
- For other regions, specify the region parameter
- Ensure AWS_REGION in .env matches your intended region

---

## Testing the Server

### Manual Testing
You can test the server directly without Claude:

```python
# test_server.py
import asyncio
import json
from aws_mcp_server.services import S3Service

async def test():
    s3 = S3Service()
    result = s3.list_buckets()
    print(json.dumps(result, indent=2))

asyncio.run(test())
```

### Testing with MCP Inspector
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector python -m aws_mcp_server.server
```

---

## Best Practices

### Security
1. **Never commit credentials** - Use `.env` file and add it to `.gitignore`
2. **Use IAM roles** when possible instead of access keys
3. **Principle of least privilege** - Only grant necessary permissions
4. **Rotate credentials** regularly
5. **Use temporary credentials** (AWS STS) for enhanced security

### Performance
1. **Use batch operations** for multiple items
2. **Set appropriate limits** on scan/query operations
3. **Use pagination** for large result sets
4. **Consider caching** for frequently accessed data

### Cost Management
1. **Use PAY_PER_REQUEST** billing for DynamoDB tables with unpredictable traffic
2. **Delete unused resources** (buckets, tables)
3. **Monitor AWS costs** regularly
4. **Use lifecycle policies** for S3 objects

---

## Support

### Getting Help
- Check the [AWS Documentation](https://docs.aws.amazon.com/)
- Review [MCP Documentation](https://modelcontextprotocol.io/)
- Open an issue on GitHub

### Useful Commands
```bash
# Check Python version
python --version

# Verify AWS credentials
aws sts get-caller-identity

# List installed packages
pip list

# Check if server module is importable
python -c "import aws_mcp_server; print('OK')"
```

---

## Next Steps

1. **Explore all 24 tools** - Try each operation
2. **Create workflows** - Combine multiple operations
3. **Add error handling** - Handle edge cases gracefully
4. **Monitor usage** - Track AWS costs and usage
5. **Contribute** - Add new features or improvements

---

## License
MIT License - See LICENSE file for details
