import boto3
from botocore.exceptions import ClientError
import subprocess
import os
from git import Repo, GitCommandError
import re

import boto3


def read_requirements_as_text(file_path):
    """
    Reads a requirements.txt file and returns its contents as a text string.
    
    Parameters:
    - file_path: The path to the requirements.txt file.
    
    Returns:
    - A string containing the contents of the requirements.txt file.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"An error occurred while reading {file_path}: {e}")
        return ""


def create_codecommit_pull_request(repository_name, source_branch, destination_branch, title, description):
    client = boto3.client('codecommit')
    
    try:
        response = client.create_pull_request(
            title=title,
            description=description,
            targets=[
                {
                    'repositoryName': repository_name,
                    'sourceReference': source_branch,
                    'destinationReference': destination_branch,
                },
            ]
        )
        print(f"Pull Request Created: {response['pullRequest']['pullRequestId']}")
    except Exception as e:
        print(f"Error creating pull request: {e}")



def update_requirements_from_text(text, repo_path, branch_name):
    # Encontra a seção de Updated Requirements.txt
    match = re.search(r'Updated `requirements\.txt`:\s*```\s*([\s\S]*?)\s*```', text, re.DOTALL)
    if not match:
        print("Não foi possível encontrar a seção de Updated Requirements.txt.")
        return False

    # Extrai o conteúdo dos requirements
    requirements_content = match.group(1).strip()
    
    # Inicializa o repositório Git
    repo = Repo(repo_path)
    
    # # Configura nome e email do usuário para o commit no repositório local
    repo.config_writer().set_value("user", "name", "CVE Finder").release()
    repo.config_writer().set_value("user", "email", "cve_finder@example.com").release()

    # # Caminho do arquivo requirements.txt no repositório
    requirements_file_path = f"{repo_path}/requirements.txt"
    
    # Escreve o novo conteúdo no arquivo requirements.txt
    with open(requirements_file_path, 'w') as file:
        file.write(requirements_content + '\n')
    
    # Faz commit das mudanças
    repo.git.add('requirements.txt')
    repo.git.commit('-m', 'Atualiza requirements.txt com versões seguras')

    # Faz push da nova branch (opcional, pode requerer configuração adicional de autenticação)
    repo.git.push('origin', branch_name)

    print(f"requirements.txt atualizado na branch '{branch_name}'.")
    return True

def clone_codecommit_repo(repo_url, local_dir, key_path):
    try:
        # Set the SSH command with the provided key and disable strict host key checking
        git_ssh_cmd = f'ssh -i {key_path} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
        
        # Prepare the command to clone the Git repository
        clone_cmd = f'GIT_SSH_COMMAND="{git_ssh_cmd}" git clone {repo_url} {local_dir}'
        
        # Execute the command
        subprocess.run(clone_cmd, shell=True, check=True)
        print(f"Repository successfully cloned into {local_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning the repository: {e}")

    

def create_and_switch_to_branch(repo_path, new_branch_name):
    try:
        # Inicializa o repositório Git no caminho especificado
        repo = Repo(repo_path)
        
        # Cria e muda para a nova branch
        new_branch = repo.create_head(new_branch_name)
        new_branch.checkout()
        
        print(f"Branch '{new_branch_name}' criada e selecionada com sucesso.")
        return True
    except GitCommandError as e:
        print(f"Erro ao criar e mudar para a branch {new_branch_name}: {e}")
        return False
    except Exception as e:
        print(f"Erro desconhecido: {e}")
        return False


