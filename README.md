## Automated vulnerability patching for secure application development

This repository contains the architecture and codebase for an automated remediation pipeline designed to address ECR Inspector findings using the power of Generative AI, specifically leveraging Amazon Bedrock's in-context learning capabilities.

### Overview

![Architecture Diagram](images/architecture-diagram.png)

The pipeline is designed to seamlessly integrate with your CI/CD workflow, providing a robust solution for vulnerability management. The diagram illustrates the complete solution, which comprises several interconnected components:

1. **CI Pipeline Integration**: Commences with a clone of the Application Repo, followed by static code analysis, image building, and local analysis using Trivy. The resultant image is then pushed to ECR.

2. **ECR and Inspector**: The ECR hosts the images, which are scanned by the Inspector. Findings are then evaluated for severity.

3. **Lambda Functions**:
    - **Aggregate Inspector Findings**: Gathers Inspector data and stores it into a DynamoDB table.
    - **Change Image Tag**: Tags the images in ECR as `prd-sha` or `risk-sha` based on Inspector findings.

4. **Amazon Bedrock with Generative AI**:
    - Receives aggregated data from the Lambda function.
    - Uses in-context learning to generate pull requests with remediation suggestions for vulnerabilities in the application repositories.

5. **ECS and Fargate Execution**: The application, with suggested fixes, is deployed using ECS and Fargate for a streamlined operation.

### Implemented Components

The current implementation focuses on three primary areas:

- **Lambda Function for Data Aggregation**: Central to the pipeline, it collects findings from Inspector and feeds them into DynamoDB.
- **Sample Applications with CVEs**: Provides real-world scenarios to test the pipeline's efficacy.
- **ECS Application with Generative AI**: Demonstrates the potential of Amazon Bedrock's AI to suggest code fixes by opening pull requests in the application repositories.

### Objective

The goal of this pipeline is to reduce the manual effort required in vulnerability remediation by automating the generation of fixes for security issues identified by ECR Inspector. It not only identifies the problems but also suggests the code changes necessary for a resolution.

### Deployment

TBD
