"""EC2 service implementation for the MCP server."""

from __future__ import annotations

import datetime as dt
import time
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from ec2_mcp_python_config import aws_config


class EC2Service:
    """Service layer responsible for interacting with EC2, SSM, and CloudWatch."""

    def __init__(self) -> None:
        config = aws_config.get_boto3_config()
        self.ec2_client = boto3.client("ec2", **config)
        self.ssm_client = boto3.client("ssm", **config)
        self.cw_client = boto3.client("cloudwatch", **config)

    # ------------------------------------------------------------------
    # EC2 instance lifecycle operations
    # ------------------------------------------------------------------
    def describe_instances(
        self,
        instance_ids: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Return details for one or more EC2 instances."""
        params: Dict[str, Any] = {}
        if instance_ids:
            params["InstanceIds"] = instance_ids
        if filters:
            params["Filters"] = filters

        try:
            paginator = self.ec2_client.get_paginator("describe_instances")
            response: List[Dict[str, Any]] = []
            for page in paginator.paginate(**params):
                response.extend(page.get("Reservations", []))
            return {"success": True, "reservations": response}
        except (ClientError, BotoCoreError) as error:
            return {"success": False, "error": str(error)}

    def start_instances(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Start the specified EC2 instances."""
        try:
            response = self.ec2_client.start_instances(InstanceIds=instance_ids)
            return {"success": True, "startingInstances": response.get("StartingInstances", [])}
        except (ClientError, BotoCoreError) as error:
            return {"success": False, "error": str(error)}

    def stop_instances(self, instance_ids: List[str], force: bool = False) -> Dict[str, Any]:
        """Stop the specified EC2 instances."""
        try:
            response = self.ec2_client.stop_instances(InstanceIds=instance_ids, Force=force)
            return {"success": True, "stoppingInstances": response.get("StoppingInstances", [])}
        except (ClientError, BotoCoreError) as error:
            return {"success": False, "error": str(error)}

    def reboot_instances(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Reboot the specified EC2 instances."""
        try:
            self.ec2_client.reboot_instances(InstanceIds=instance_ids)
            return {"success": True, "rebootedInstances": instance_ids}
        except (ClientError, BotoCoreError) as error:
            return {"success": False, "error": str(error)}

    def terminate_instances(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Terminate the specified EC2 instances."""
        try:
            response = self.ec2_client.terminate_instances(InstanceIds=instance_ids)
            return {"success": True, "terminatingInstances": response.get("TerminatingInstances", [])}
        except (ClientError, BotoCoreError) as error:
            return {"success": False, "error": str(error)}

    def get_instance_status(
        self,
        instance_ids: Optional[List[str]] = None,
        include_all_instances: bool = False,
    ) -> Dict[str, Any]:
        """Retrieve instance status checks."""
        params: Dict[str, Any] = {"IncludeAllInstances": include_all_instances}
        if instance_ids:
            params["InstanceIds"] = instance_ids

        try:
            response = self.ec2_client.describe_instance_status(**params)
            return {"success": True, "instanceStatuses": response.get("InstanceStatuses", [])}
        except (ClientError, BotoCoreError) as error:
            return {"success": False, "error": str(error)}

    # ------------------------------------------------------------------
    # SSM command execution ("login")
    # ------------------------------------------------------------------
    def run_command(
        self,
        instance_ids: List[str],
        command: str,
        document_name: str = "AWS-RunShellScript",
        comment: Optional[str] = None,
        execution_timeout: int = 600,
        wait_for_completion: bool = True,
        poll_interval: float = 2.0,
    ) -> Dict[str, Any]:
        """Execute a shell command on instances using AWS Systems Manager."""
        try:
            params: Dict[str, Any] = {
                "InstanceIds": instance_ids,
                "DocumentName": document_name,
                "Parameters": {"commands": [command]},
                "TimeoutSeconds": execution_timeout,
            }
            if comment:
                params["Comment"] = comment

            response = self.ssm_client.send_command(**params)
            command_id = response.get("Command", {}).get("CommandId")
            result: Dict[str, Any] = {"success": True, "commandId": command_id}

            if wait_for_completion and command_id:
                target_count = len(instance_ids)
                completed: set[str] = set()
                invocation_summaries: Dict[str, Dict[str, Any]] = {}

                while len(completed) < target_count:
                    time.sleep(poll_interval)
                    for instance_id in instance_ids:
                        if instance_id in completed:
                            continue
                        try:
                            invocation = self.ssm_client.get_command_invocation(
                                CommandId=command_id,
                                InstanceId=instance_id,
                            )
                        except ClientError as error:
                            if error.response.get("Error", {}).get("Code") == "InvocationDoesNotExist":
                                continue
                            raise

                        status = invocation.get("Status")
                        if status in {"Success", "Cancelled", "Failed", "TimedOut", "Cancelling"}:
                            completed.add(instance_id)

                        invocation_record = invocation.copy()
                        invocation_record["InstanceId"] = instance_id
                        invocation_summaries[instance_id] = invocation_record

                result["invocations"] = list(invocation_summaries.values())

            return result
        except (ClientError, BotoCoreError) as error:
            return {"success": False, "error": str(error)}

    # ------------------------------------------------------------------
    # CloudWatch metrics
    # ------------------------------------------------------------------
    def get_instance_metrics(
        self,
        instance_id: str,
        period: int = 300,
        lookback_minutes: int = 10,
    ) -> Dict[str, Any]:
        """Fetch recent CPU and memory utilization metrics for an instance."""
        end_time = dt.datetime.utcnow()
        start_time = end_time - dt.timedelta(minutes=lookback_minutes)

        try:
            cpu_datapoints = self._get_metric_datapoints(
                namespace="AWS/EC2",
                metric_name="CPUUtilization",
                dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                start_time=start_time,
                end_time=end_time,
                period=period,
                statistics=["Average", "Maximum"],
            )

            memory_datapoints = self._get_metric_datapoints(
                namespace="CWAgent",
                metric_name="mem_used_percent",
                dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                start_time=start_time,
                end_time=end_time,
                period=period,
                statistics=["Average", "Maximum"],
            )

            if not memory_datapoints:
                memory_datapoints = self._get_metric_datapoints(
                    namespace="System/Linux",
                    metric_name="MemoryUtilization",
                    dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    start_time=start_time,
                    end_time=end_time,
                    period=period,
                    statistics=["Average", "Maximum"],
                )

            return {
                "success": True,
                "cpuUtilization": cpu_datapoints,
                "memoryUtilization": memory_datapoints,
                "note": "Memory metrics require the CloudWatch agent."
                if not memory_datapoints
                else None,
            }
        except (ClientError, BotoCoreError) as error:
            return {"success": False, "error": str(error)}

    def _get_metric_datapoints(
        self,
        *,
        namespace: str,
        metric_name: str,
        dimensions: List[Dict[str, str]],
        start_time: dt.datetime,
        end_time: dt.datetime,
        period: int,
        statistics: List[str],
    ) -> List[Dict[str, Any]]:
        """Helper for retrieving CloudWatch metric statistics."""
        response = self.cw_client.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=statistics,
        )
        datapoints = response.get("Datapoints", [])
        datapoints.sort(key=lambda point: point.get("Timestamp"))
        for datapoint in datapoints:
            timestamp = datapoint.get("Timestamp")
            if isinstance(timestamp, dt.datetime):
                datapoint["Timestamp"] = timestamp.isoformat()
        return datapoints
