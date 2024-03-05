import boto3
import json
from pr_opener import *
import os

incontext_learning = """
Application: in-context-learning-example
Vulnerabilities:
- Werkzeug 1.0.1 (fixed in 2.2.3): CVE CVE-2023-25577
- urllib3 1.25.11 (fixed in 2.0.7): CVE CVE-2023-45803
- Jinja2 2.11.2 (fixed in 2.11.3): CVE CVE-2020-28493
- pip 23.0.1 (fixed in 23.3): CVE CVE-2023-5752
- requests 2.24.0 (fixed in 2.31.0): CVE CVE-2023-32681
- setuptools 57.5.0 (fixed in 65.5.1): CVE CVE-2022-40897
- Flask 1.1.2 (fixed in 2.3.2): CVE CVE-2023-30861

Current `requirements.txt`:
```
Flask==1.1.2
Jinja2==2.11.2
Werkzeug==1.0.1
requests==2.24.0
```

Suggestions for improvement:
To enhance the security and maintain the integrity of your Python application, it's critical to address the following package vulnerabilities by updating to the recommended versions. Each update mitigates specific security risks associated with these packages, ensuring your application is safeguarded against potential exploits:

- **Flask 1.1.2**: Update to Flask==2.3.2 to resolve CVE-2023-30861, which addresses a security flaw that could allow unauthorized access or data leakage.
- **Jinja2 2.11.2**: Upgrade to Jinja2==3.1.3 to fix vulnerabilities CVE-2020-28493 and CVE-2024-22195. These updates patch security issues that could lead to remote code execution or information disclosure.
- **Werkzeug 1.0.1**: Upgrade to Werkzeug==3.0.1 to mitigate CVE-2023-25577, CVE-2023-23934, and CVE-2023-46136. These updates close security gaps that could be exploited to perform denial of service attacks or unauthorized actions.
- **requests 2.24.0**: Update to requests==2.31.0 to address CVE-2023-32681, fixing a vulnerability that could allow attackers to disclose sensitive information.
- **urllib3 1.25.11**: Upgrade to urllib3==2.0.7 to resolve CVE-2023-45803, CVE-2023-43804, and CVE-2021-33503, mitigating issues that could lead to information leakage or denial of service.
- **pip 23.0.1**: Update to pip==23.3 to fix CVE-2023-5752, addressing a vulnerability that could impact package integrity verification.
- **setuptools 57.5.0**: Upgrade to setuptools==65.5.1 to correct CVE-2022-40897, which resolves a flaw that could allow unauthorized code execution during package installation.

Action Steps:
1. Review your `requirements.txt` and update the versions of the aforementioned packages to their secure versions as listed.
2. After updating, run thorough tests to ensure that the upgrades do not disrupt your application functionalities.
3. Regularly monitor and review security advisories for your application's dependencies to proactively address new vulnerabilities as they are discovered.

Updated `requirements.txt`:
```
Flask==2.3.2
Jinja2==3.1.3
Werkzeug==3.0.1
requests==2.31.0
urllib3==2.0.7
pip==23.3
setuptools==65.5.1
```
---
"""

def get_vulnerabilities_from_dynamo(ecr_repo_name, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        response = table.get_item(Key={'ecr_repo_name': ecr_repo_name})
        if 'Item' in response:
            return response['Item']
        else:
            return None
    except Exception as e:
        print(f"Erro ao acessar DynamoDB: {str(e)}") 
        return None

def build_model_prompt(vulnerabilities_item, requirements, app_name):
    prompt = f"Application:{app_name}\nVulnerabilities:\n"
    
    for vulnerability in vulnerabilities_item.get('vulnerabilities', []):
        if vulnerability.get('library_name') not in prompt:
            prompt += f"- {vulnerability['library_name']} {vulnerability['current_version']} (fixed in {vulnerability['fixed_in_version']}): CVE {vulnerability['cve_id']}\n"
    
    prompt += f"\nCurrent `requirements.txt`:\n```\n{requirements}\n```\nSuggestions for improvement:"
    return prompt

def invoke_bedrock_model(prompt):
    brt = boto3.client(service_name='bedrock-runtime')
    body = json.dumps({
    "prompt": f"{prompt}",
    "max_gen_len": 2048,
    "temperature": 0.5,
    "top_p": 0.9,
    })
    modelId = 'meta.llama2-13b-chat-v1'
    accept = 'application/json'
    contentType = 'application/json'

    response = brt.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    return response_body.get('generation')

def main():
    ecr_repo_name = os.getenv("ECR_REPO_NAME", "my-amazing-application") # Needs to be dynamic and get by event
    table_name = 'aggregate-cve-results'
    repo_url = f"ssh://APKAQZOY3J3EYI726W6Q@git-codecommit.us-west-2.amazonaws.com/v1/repos/{ecr_repo_name}"
    local_dir = f"/tmp/{ecr_repo_name}"
    new_branch_name = 'cve_finder'
    key_path = "/root/.ssh/id_rsa" # Internal key in the container
    requirements_updated = False
    model_analysis_completion = ""
    vulnerabilities_item = get_vulnerabilities_from_dynamo(ecr_repo_name, table_name)

    if vulnerabilities_item:
        # Need to clone first to get requirements dependencyx
        clone_codecommit_repo(repo_url, local_dir, key_path)
        
        requirements_file = read_requirements_as_text(f"{local_dir}/requirements.txt")
        model_prompt = build_model_prompt(vulnerabilities_item, requirements_file, ecr_repo_name)
        final_model_prompt = incontext_learning + model_prompt
        
        while requirements_updated == False:
            model_analysis_completion = invoke_bedrock_model(final_model_prompt)
            print(model_analysis_completion)
            create_and_switch_to_branch(local_dir, new_branch_name)
            requirements_updated = update_requirements_from_text(model_analysis_completion, local_dir, new_branch_name)
        
        repository_name = ecr_repo_name
        source_branch = new_branch_name
        destination_branch = 'main'
        title = 'CVE Finder, please take a look and update with the following recommendations'
        description = model_analysis_completion

        create_codecommit_pull_request(repository_name, source_branch, destination_branch, title, description)


# Write main init for python
if __name__ == "__main__":
    main()