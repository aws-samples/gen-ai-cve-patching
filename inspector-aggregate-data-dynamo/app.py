import json
import boto3
from botocore.exceptions import ClientError

def get_vulnerability_details(json_data):
    vulnerability_info = {
        'library_name': None,
        'current_version': None,
        'fixed_in_version': None,
        'cve_id': None,
        'ecr_repository_name': None
    }
    
   # Get ECR repo name
    if 'resources' in json_data and json_data['resources']:
        resource_arn = json_data['resources'][0]
        repo_name_with_hash = resource_arn.split(':repository/')[-1]
        repo_name = repo_name_with_hash.split('/')[0]
        vulnerability_info['ecr_repository_name'] = repo_name
    
    # Get package vulnerability
    if 'detail' in json_data and 'packageVulnerabilityDetails' in json_data['detail']:
        details = json_data['detail']['packageVulnerabilityDetails']
        
        if 'vulnerablePackages' in details and details['vulnerablePackages']:
            vulnerable_package = details['vulnerablePackages'][0]
            vulnerability_info['library_name'] = vulnerable_package['name']
            vulnerability_info['current_version'] = vulnerable_package['version']
            vulnerability_info['fixed_in_version'] = vulnerable_package['fixedInVersion']
            vulnerability_info['cve_id'] = details['vulnerabilityId']

    return vulnerability_info


def update_cve_details(ecr_repo_name, vulnerability_info, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        # Primeiro, tente recuperar o item atual para verificar se a vulnerabilidade já existe
        current_item = table.get_item(Key={'ecr_repo_name': ecr_repo_name})
        if 'Item' in current_item and 'vulnerabilities' in current_item['Item']:
            vulnerabilities = current_item['Item']['vulnerabilities']
            if vulnerability_info in vulnerabilities:
                print("Vulnerability info already exists. No update needed.")
                return
        # Se a informação da vulnerabilidade não existe, atualize o item
        response = table.update_item(
            Key={'ecr_repo_name': ecr_repo_name},
            UpdateExpression="SET #vulnerabilities = list_append(if_not_exists(#vulnerabilities, :empty_list), :vulnerability)",
            ExpressionAttributeNames={'#vulnerabilities': 'vulnerabilities'},
            ExpressionAttributeValues={
                ':vulnerability': [vulnerability_info],
                ':empty_list': []
            },
            ReturnValues="UPDATED_NEW"
        )
        print("Item updated successfully:", response)
    except ClientError as e:
        print("Error updating item:", e)
        
def lambda_handler(event, context):
    vulnerability_details = get_vulnerability_details(event)
    ecr_repo_name = vulnerability_details['ecr_repository_name']
    dynamo_db_table_name = "aggregate-cve-results"
    
    # Removing Key from dict
    del vulnerability_details['ecr_repository_name']
    result = update_cve_details(ecr_repo_name, vulnerability_details, dynamo_db_table_name)
    print(result)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from Lambda!',
            'vulnerability_details': vulnerability_details
        })
    }