"""S3 service implementation."""

from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import ClientError
from aws_mcp_python_config import aws_config


class S3Service:
    """Service for S3 operations."""

    def __init__(self) -> None:
        self.client = boto3.client("s3", **aws_config.get_boto3_config())

    def create_bucket(self, bucket_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """Create a new S3 bucket."""
        try:
            create_bucket_config = {}
            bucket_region = region or aws_config.region
            
            # LocationConstraint is not needed for us-east-1
            if bucket_region != "us-east-1":
                create_bucket_config["CreateBucketConfiguration"] = {
                    "LocationConstraint": bucket_region
                }

            response = self.client.create_bucket(
                Bucket=bucket_name,
                **create_bucket_config
            )
            
            return {
                "success": True,
                "bucketName": bucket_name,
                "location": response.get("Location"),
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def list_buckets(self) -> Dict[str, Any]:
        """List all S3 buckets."""
        try:
            response = self.client.list_buckets()
            buckets = [
                {
                    "name": bucket["Name"],
                    "creationDate": bucket["CreationDate"].isoformat(),
                }
                for bucket in response.get("Buckets", [])
            ]
            return {"buckets": buckets}
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def delete_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """Delete an S3 bucket."""
        try:
            self.client.delete_bucket(Bucket=bucket_name)
            return {
                "success": True,
                "bucketName": bucket_name,
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def upload_object(
        self,
        bucket_name: str,
        key: str,
        content: str,
        content_type: str = "text/plain",
    ) -> Dict[str, Any]:
        """Upload an object to S3."""
        try:
            response = self.client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content.encode("utf-8"),
                ContentType=content_type,
            )
            return {
                "success": True,
                "bucketName": bucket_name,
                "key": key,
                "etag": response.get("ETag"),
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def delete_object(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """Delete an object from S3."""
        try:
            self.client.delete_object(Bucket=bucket_name, Key=key)
            return {
                "success": True,
                "bucketName": bucket_name,
                "key": key,
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
    ) -> Dict[str, Any]:
        """List objects in an S3 bucket."""
        try:
            params = {
                "Bucket": bucket_name,
                "MaxKeys": max_keys,
            }
            if prefix:
                params["Prefix"] = prefix

            response = self.client.list_objects_v2(**params)
            
            objects = [
                {
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "lastModified": obj["LastModified"].isoformat(),
                    "etag": obj.get("ETag"),
                }
                for obj in response.get("Contents", [])
            ]
            
            return {
                "objects": objects,
                "keyCount": response.get("KeyCount", 0),
                "isTruncated": response.get("IsTruncated", False),
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def read_object(self, bucket_name: str, key: str) -> Dict[str, Any]:
        """Read an object's content from S3."""
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=key)
            content = response["Body"].read().decode("utf-8")
            
            return {
                "success": True,
                "bucketName": bucket_name,
                "key": key,
                "content": content,
                "contentType": response.get("ContentType"),
                "contentLength": response.get("ContentLength"),
                "lastModified": response.get("LastModified").isoformat() if response.get("LastModified") else None,
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
            }
