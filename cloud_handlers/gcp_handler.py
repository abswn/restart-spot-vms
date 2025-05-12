import os
from loguru import logger
from google.cloud import compute_v1

def start_vm(project_id: str, zone: str, instance_name: str, credentials_file: str) -> bool:
    """
    Start a VM instance.

    Args:
        project_id (str): Google Cloud project ID.
        zone (str): The zone where the VM instance is located.
        instance_name (str): The name of the VM instance.
        credentials_file (str): Name of the credentials file in credentials directory.

    Returns:
        bool: True if the VM instance was started successfully, False otherwise.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
    instance_client = compute_v1.InstancesClient()
    try:
        logger.info (f"Starting VM: {instance_name} in {zone}...")
        request = compute_v1.StartInstanceRequest(
            project=project_id,
            zone=zone,
            instance=instance_name
        )
        operation = instance_client.start(request=request)
        operation.result()  # Wait for the operation to complete
        return True
    except Exception as e:
        logger.error(f"Error starting VM {instance_name}: {e}")
        return False

def is_vm_terminated(project_id: str, zone: str, instance_name: str, credentials_file: str) -> bool:
    """
    Check if a VM instance is terminated.

    Args:
        project_id (str): Google Cloud project ID.
        zone (str): The zone where the VM instance is located.
        instance_name (str): The name of the VM instance.
        credentials_file (str): Name of the credentials file in credentials directory.

    Returns:
        bool: True if the VM instance is terminated, False otherwise.
        
    Note:
        Returns False if there's an error checking the VM status.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
    instance_client = compute_v1.InstancesClient()
    try:
        request = compute_v1.GetInstanceRequest(
            project=project_id,
            zone=zone,
            instance=instance_name
        )
        instance = instance_client.get(request=request)
        return instance.status == "TERMINATED"
    except Exception as e:
        logger.error(f"Error checking status for VM {instance_name}: {e}")
        return False
