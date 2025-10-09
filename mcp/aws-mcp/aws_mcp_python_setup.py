"""Setup script defining packaging configuration for the AWS MCP server."""

from setuptools import setup, find_packages

setup(
    name="aws-mcp-server",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
)
