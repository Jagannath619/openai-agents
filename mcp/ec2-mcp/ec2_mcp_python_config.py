"""Configuration management for EC2 MCP Server."""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class AWSConfig:
    """AWS configuration settings for EC2 and supporting services."""

    def __init__(self) -> None:
        self.region: str = os.getenv("AWS_REGION", "us-east-1")
        self.access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.session_token: Optional[str] = os.getenv("AWS_SESSION_TOKEN")

    def get_boto3_config(self) -> dict[str, str]:
        """Return a configuration dictionary for boto3 clients."""
        config: dict[str, str] = {"region_name": self.region}

        if self.access_key_id and self.secret_access_key:
            config["aws_access_key_id"] = self.access_key_id
            config["aws_secret_access_key"] = self.secret_access_key
            if self.session_token:
                config["aws_session_token"] = self.session_token

        return config


aws_config = AWSConfig()
