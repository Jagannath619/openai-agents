# AWS VPC MCP Server

A Model Context Protocol (MCP) server that provides AWS VPC management capabilities to Claude Desktop. This server enables Claude to create, manage, and configure AWS VPC resources through natural language conversations.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Contributing](#contributing)
- [License](#license)

## Features

This MCP server provides comprehensive AWS VPC management capabilities:

- **VPC Management**: Create, delete, and describe VPCs
- **Subnet Management**: Create, delete, and describe subnets
- **Internet Gateway**: Create, delete, attach, and detach internet gateways
- **Route Tables**: Create, delete, associate, and disassociate route tables
- **Security Groups**: Create, delete, describe, and manage ingress rules

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
- **Claude Desktop** (latest version)
- **AWS Account** with appropriate permissions
- **AWS Credentials** (Access Key ID and Secret Access Key)

### Required AWS Permissions

Your AWS IAM user or role should have the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:DescribeVpcs",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:DescribeSubnets",
        "ec2:CreateInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DetachInternetGateway",
        "ec2:CreateRouteTable",
        "ec2:DeleteRouteTable",
        "ec2:AssociateRouteTable",
        "ec2:DisassociateRouteTable",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:DescribeSecurityGroups",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupIngress"
      ],
      "Resource": "*"
    }
  ]
}
```

## Installation

### Step 1: Clone or Download the Project

```bash
# Create a project directory
mkdir aws-vpc-mcp-server
cd aws-vpc-mcp-server

# Copy all project files to this directory
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `mcp>=1.0.0` - Model Context Protocol SDK
- `boto3>=1.35.0` - AWS SDK for Python
- `python-dotenv>=1.0.0` - Environment variable management

## Configuration

### Step 1: Create Environment File

Create a `.env` file in your project root directory:

```bash
# .env file
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Optional: Only needed for temporary credentials
# AWS_SESSION_TOKEN=your_session_token_here
```

**Important:** Replace the placeholder values with your actual AWS credentials.

### Step 2: Configure Claude Desktop

You need to register your MCP server with Claude Desktop by editing its configuration file.

#### Configuration File Locations:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

#### Add Your Server Configuration:

Open the configuration file and add your server. If the file doesn't exist, create it with this content:

**Recommended Approach (Using Virtual Environment Python):**

```json
{
  "mcpServers": {
    "aws-vpc": {
      "command": "/absolute/path/to/your/project/venv/bin/python",
      "args": [
        "/absolute/path/to/your/project/vpc_mcp_python_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Real Example (macOS/Linux):**
```json
{
  "mcpServers": {
    "aws-vpc": {
      "command": "/Users/jagannathpanda/aws-vpc-mcp/venv/bin/python",
      "args": [
        "/Users/jagannathpanda/aws-vpc-mcp/vpc_mcp_python_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Real Example (Windows):**
```json
{
  "mcpServers": {
    "aws-vpc": {
      "command": "C:/Users/YourName/aws-vpc-mcp/venv/Scripts/python.exe",
      "args": [
        "C:/Users/YourName/aws-vpc-mcp/vpc_mcp_python_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Important Notes:**
1. Use the **full absolute path** to the Python executable in your virtual environment
2. Use the **full absolute path** to your server file
3. On **macOS/Linux**: Use `venv/bin/python`
4. On **Windows**: Use `venv\Scripts\python.exe` (but with forward slashes `/` in the JSON)
5. `PYTHONUNBUFFERED=1` ensures real-time logging output

**How to Find Your Absolute Paths:**

```bash
# On macOS/Linux - Run in your project directory:
pwd  # Shows current directory path
# Then use: /output/from/pwd/venv/bin/python

# On Windows - Run in your project directory:
cd  # Shows current directory path
# Then use: C:/output/from/cd/venv/Scripts/python.exe
```

#### Alternative: Embedding AWS Credentials in Config

If you prefer NOT to use a `.env` file, you can add AWS credentials directly:

```json
{
  "mcpServers": {
    "aws-vpc": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": [
        "/absolute/path/to/vpc_mcp_python_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "your_access_key_here",
        "AWS_SECRET_ACCESS_KEY": "your_secret_key_here"
      }
    }
  }
}
```

**⚠️ Security Warning:** This approach exposes credentials in the config file. Using a `.env` file is more secure.

### Step 3: Restart Claude Desktop

After editing the configuration file:

1. **Completely quit** Claude Desktop (don't just close the window)
2. **Restart** Claude Desktop
3. Look for the 🔨 (hammer) icon in the input box - this indicates MCP tools are loaded

## Usage

Once configured, you can interact with your AWS VPC resources through natural language in Claude Desktop.

### Basic Usage Pattern

Simply ask Claude to perform VPC operations:

```
You: "Create a new VPC with CIDR block 10.0.0.0/16"

Claude: [Uses the vpc_create tool and returns the VPC details]
```

### Checking Tool Availability

To verify your MCP server is working:

```
You: "What AWS VPC tools do you have available?"

Claude: [Lists all available VPC management tools]
```

## Available Tools

### VPC Operations

#### `vpc_create`
Creates a new VPC with specified CIDR block.

**Parameters:**
- `cidrBlock` (required): CIDR block for the VPC (e.g., "10.0.0.0/16")
- `instanceTenancy` (optional): Instance tenancy option ("default", "dedicated", "host")
- `amazonProvidedIpv6` (optional): Request Amazon-provided IPv6 CIDR block

#### `vpc_delete`
Deletes a specified VPC.

**Parameters:**
- `vpcId` (required): ID of the VPC to delete

#### `vpc_describe`
Describes one or more VPCs.

**Parameters:**
- `vpcIds` (optional): List of VPC IDs to describe
- `filters` (optional): Filters to apply

### Subnet Operations

#### `subnet_create`
Creates a subnet in a VPC.

**Parameters:**
- `vpcId` (required): ID of the VPC
- `cidrBlock` (required): CIDR block for the subnet
- `availabilityZone` (optional): Availability Zone
- `ipv6CidrBlock` (optional): IPv6 CIDR block

#### `subnet_delete`
Deletes a subnet.

**Parameters:**
- `subnetId` (required): ID of the subnet to delete

#### `subnet_describe`
Describes subnets.

**Parameters:**
- `subnetIds` (optional): List of subnet IDs
- `filters` (optional): Filters to apply

### Internet Gateway Operations

#### `internet_gateway_create`
Creates an internet gateway.

**Parameters:** None

#### `internet_gateway_delete`
Deletes an internet gateway.

**Parameters:**
- `internetGatewayId` (required): ID of the internet gateway

#### `internet_gateway_attach`
Attaches an internet gateway to a VPC.

**Parameters:**
- `internetGatewayId` (required): ID of the internet gateway
- `vpcId` (required): ID of the VPC

#### `internet_gateway_detach`
Detaches an internet gateway from a VPC.

**Parameters:**
- `internetGatewayId` (required): ID of the internet gateway
- `vpcId` (required): ID of the VPC

### Route Table Operations

#### `route_table_create`
Creates a route table.

**Parameters:**
- `vpcId` (required): ID of the VPC

#### `route_table_delete`
Deletes a route table.

**Parameters:**
- `routeTableId` (required): ID of the route table

#### `route_table_associate`
Associates a route table with a subnet.

**Parameters:**
- `routeTableId` (required): ID of the route table
- `subnetId` (required): ID of the subnet

#### `route_table_disassociate`
Disassociates a route table from a subnet.

**Parameters:**
- `associationId` (required): Association ID

### Security Group Operations

#### `security_group_create`
Creates a security group.

**Parameters:**
- `groupName` (required): Name of the security group
- `description` (required): Description
- `vpcId` (required): VPC ID

#### `security_group_delete`
Deletes a security group.

**Parameters:**
- `groupId` (required): ID of the security group

#### `security_group_describe`
Describes security groups.

**Parameters:**
- `groupIds` (optional): List of security group IDs
- `filters` (optional): Filters to apply

#### `security_group_authorize_ingress`
Authorizes security group ingress rules.

**Parameters:**
- `groupId` (required): Security group ID
- `ipPermissions` (required): List of IP permission objects

#### `security_group_revoke_ingress`
Revokes security group ingress rules.

**Parameters:**
- `groupId` (required): Security group ID
- `ipPermissions` (required): List of IP permission objects to revoke

## Examples

### Example 1: Create a Basic VPC Setup

```
You: "Create a VPC with CIDR 10.0.0.0/16, then create two subnets: 
     one public (10.0.1.0/24) and one private (10.0.2.0/24)"

Claude: [Creates VPC and subnets, provides IDs]
```

### Example 2: Set Up Internet Access

```
You: "For VPC vpc-12345, create an internet gateway and attach it"

Claude: [Creates IGW and attaches to VPC]
```

### Example 3: Configure Security Group

```
You: "Create a security group called 'web-sg' in vpc-12345 that allows 
     HTTP (port 80) and HTTPS (port 443) from anywhere"

Claude: [Creates security group with appropriate rules]
```

### Example 4: Query Existing Resources

```
You: "Show me all VPCs in my account"

Claude: [Lists all VPCs with details]
```

### Example 5: Complex Infrastructure Setup

```
You: "I need a complete VPC setup with:
     - VPC with CIDR 10.0.0.0/16
     - Public subnet in us-east-1a
     - Private subnet in us-east-1b
     - Internet gateway attached
     - Security group for web servers"

Claude: [Creates all resources step by step]
```

## Troubleshooting

### Server Not Appearing in Claude Desktop

**Problem:** The 🔨 hammer icon doesn't appear.

**Solutions:**
1. Check that the path in `claude_desktop_config.json` is correct and absolute
2. Ensure Claude Desktop was completely restarted (quit, not just closed)
3. Check the Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`
4. Verify Python is in your PATH or use absolute path to Python executable

### Authentication Errors

**Problem:** "Unable to locate credentials" error.

**Solutions:**
1. Verify `.env` file exists and contains correct credentials
2. Check that AWS credentials in `claude_desktop_config.json` are correct
3. Ensure credentials have not expired (for temporary credentials)
4. Test credentials using AWS CLI: `aws sts get-caller-identity`

### Permission Denied Errors

**Problem:** "UnauthorizedOperation" or similar AWS errors.

**Solutions:**
1. Verify your IAM user/role has necessary permissions (see Prerequisites)
2. Check AWS CloudTrail for detailed error messages
3. Ensure you're operating in the correct AWS region

### Module Import Errors

**Problem:** "ModuleNotFoundError" when starting server.

**Solutions:**
1. Ensure virtual environment is activated
2. Run `pip install -r requirements.txt` again
3. Use absolute path to Python in virtual environment in config

### Connection Timeout

**Problem:** Operations timeout or hang.

**Solutions:**
1. Check your internet connection
2. Verify AWS region is correct and accessible
3. Check if there are AWS service issues in your region
4. Try increasing timeout in boto3 configuration

### Debugging Tips

1. **Check Server Logs:**
   ```bash
   # Run server directly to see errors
   python vpc_mcp_python_server.py
   ```

2. **Test AWS Connection:**
   ```python
   import boto3
   from vpc_mcp_python_config import aws_config
   
   client = boto3.client('ec2', **aws_config.get_boto3_config())
   print(client.describe_vpcs())
   ```

3. **Validate Configuration:**
   ```bash
   # Check if config file is valid JSON
   python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

## Security Best Practices

### 1. Credential Management

- **Never commit credentials** to version control
- Add `.env` to `.gitignore`
- Use IAM roles when possible (e.g., on EC2 instances)
- Rotate credentials regularly
- Use temporary credentials when available

### 2. Least Privilege Principle

- Grant only necessary permissions
- Create specific IAM policies for this tool
- Consider using separate IAM users for different projects

### 3. Environment Isolation

- Use separate AWS accounts for dev/staging/production
- Use different credentials for different environments
- Consider AWS Organizations for account management

### 4. Monitoring and Auditing

- Enable AWS CloudTrail for API call logging
- Set up CloudWatch alarms for unusual activity
- Regularly review IAM access patterns

### 5. Network Security

- Use VPC endpoints when possible
- Implement proper security group rules
- Follow AWS Well-Architected Framework guidelines

### Create .gitignore

Always create a `.gitignore` file:

```
# Environment variables
.env
.env.local
.env.*.local

# Virtual environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

## Project Structure

```
aws-vpc-mcp-server/
├── vpc_mcp_python_server.py      # Main MCP server
├── vpc_mcp_python_vpc_service.py # VPC service layer
├── vpc_mcp_python_vpc_tools.py   # Tool definitions
├── vpc_mcp_python_config.py      # Configuration management
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (create this)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue describing the bug
2. **Suggest Features**: Open an issue with your feature idea
3. **Submit Pull Requests**: Fork, create a branch, and submit a PR

### Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd aws-vpc-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [Claude Desktop MCP documentation](https://docs.claude.com)
3. Check [AWS boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
4. Open an issue on the project repository

## Acknowledgments

- Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Uses [boto3](https://boto3.amazonaws.com/) for AWS integration
- Designed for [Claude Desktop](https://claude.ai/)

## Version History

- **v1.0.0** - Initial release with core VPC management features

---

**Note:** This MCP server makes real changes to your AWS account. Always review operations before confirming, and test in a non-production environment first.