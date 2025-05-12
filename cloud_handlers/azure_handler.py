import os
import json
from loguru import logger
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

def get_azure_client(credentials_file: str) -> ComputeManagementClient:
    """
    Get Azure Compute Management Client using credentials from a JSON file.

    Args:
        credentials_file (str): Path to the credentials JSON file.

    Returns:
        ComputeManagementClient: Azure Compute Management Client.
    """
    with open(credentials_file) as file:
        credentials = json.load(file)
    os.environ.update({key: value for key, value in credentials.items() if key in ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"]})

    # Authenticate and create compute client
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, credentials["AZURE_SUBSCRIPTION_ID"])
    return compute_client

def start_vm(resource_group: str, instance_name: str, credentials_file: str) -> bool:
    """
    Start an Azure VM instance.

    Args:
        resource_group (str): The resource group of the VM.
        instance_name (str): The name of the VM instance.
        credentials_file (str): Path to the credentials JSON file.

    Returns:
        bool: True if the VM instance was started successfully, False otherwise.
    """
    compute_client = get_azure_client(credentials_file)
    try:
        logger.info(f"Starting VM: {instance_name} ...")
        async_vm_start = compute_client.virtual_machines.begin_start(resource_group, instance_name)
        async_vm_start.wait()  # Wait for the VM to start
        return True
    except Exception as e:
        logger.error(f"Error starting VM {instance_name}: {e}")
        return False

def is_vm_terminated(resource_group: str, instance_name: str, credentials_file: str) -> bool:
    """
    Check if an Azure VM instance is deallocated (terminated).

    Args:
        resource_group (str): The resource group of the VM.
        instance_name (str): The name of the VM instance.
        credentials_file (str): Path to the credentials JSON file.

    Returns:
        bool: True if the VM instance is deallocated, False otherwise.

    Note:
        Returns False if there's an error checking the VM status.
    """
    compute_client = get_azure_client(credentials_file)
    try:
        # Get the VM instance
        vm = compute_client.virtual_machines.get(resource_group, instance_name, expand="instanceView")

        # Check the power state
        for status in vm.instance_view.statuses:
            if status.code == "PowerState/deallocated":
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking status for VM {instance_name}: {e}")
        return False
