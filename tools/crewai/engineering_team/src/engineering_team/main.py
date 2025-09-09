#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from engineering_team.crew import EngineeringTeam

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

requirements = """
Build a simple AWS Cost & Resource Optimizer App with a clean UI.
The app should allow user authentication (email and password, plus option to securely add AWS access keys).
The home dashboard should display a monthly AWS cost trend line chart, the top 3 most expensive services as cards, and a list of AI-recommended savings opportunities.
A Cost Explorer screen should provide dropdown filters by service (EC2, S3, RDS, Lambda, etc.) and time range (last 7 days, 30 days, custom).
It should display a bar chart of service costs and a table of daily usage costs.
An Optimizations screen should show AI-driven suggestions for cost savings, such as identifying idle EC2 instances, underutilized RDS databases, unused Elastic IPs, and S3 buckets with old or unaccessed data.
Each suggestion should include estimated monthly savings and a recommended action.
A Resource Overview screen should list active AWS resources grouped by service.
Each resource card should show the resource ID, name, region, monthly cost estimate, and status.
A Settings screen should let users update AWS credentials, select default currency (USD, EUR, etc.), and toggle dark mode.
The UI should be simple and responsive with navigation tabs (Dashboard, Cost Explorer, Optimizations, Resources, Settings).
The UI should use charts for visualizations and cards/tables for details.
The backend should be built with Python (Flask or FastAPI).
The frontend should use a minimal UI (HTML/CSS/JS or lightweight framework).
Gradle should be used for build integration.
SQLite or PostgreSQL should be used for data storage.
AWS SDK (boto3) should be used to fetch cost and resource data.
AI agent logic should provide optimization recommendations.
The typical user flow is: user logs in, views Dashboard with costs and savings, navigates to Optimizations to see suggestions, browses Resources for details, and updates settings as needed.
"""
module_name = "aws_cost_optimizer.py"
class_name = "AWSOptimizer"


def run():
    """
    Run the research crew.
    """
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }

    # Create and run the crew
    result = EngineeringTeam().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()