import time
import os
import json
from typing import Dict, List
from loguru import logger
from cloud_handlers import gcp_handler, azure_handler

CREDENTIALS_DIR = "credentials"
SLEEP_DURATION = 300 # 5 minutes

def load_vms(json_file: str) -> Dict[str, List[dict]]:
    """
    Load VM configs from a JSON file.

    Args:
        json_file (str): Path to the JSON file containing VM instance data.

    Returns:
        dict: Dictionary with keys 'gcp', 'aws', 'azure', each mapping to a list of VM configs.
    """
    try:
        with open(json_file, 'r') as f:
            vms = json.load(f)
            return vms
    except FileNotFoundError:
        logger.error(f"File {json_file} not found.")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file {json_file}.")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {}

def main():

    logger.info("Starting script - RESTART-SPOT-VMS")
    vms = load_vms("vms.json")
    if not vms:
        logger.error("No VM instances found to process.")
        return
    logger.info(f"No. of GCP VMs: {len(vms.get('gcp', []))}")
    logger.info(f"No. of AWS VMs: {len(vms.get('aws', []))}")
    logger.info(f"No. of Azure VMs: {len(vms.get('azure', []))}")
    
    # Start monitoring
    while True:
        # GCP VMs
        for vm in vms.get("gcp", []):
            project_id = vm.get("project_id")
            zone = vm.get("zone")
            instance_name = vm.get("instance_name")
            credentials_file_name = vm.get("credentials_file")

            if not project_id or not zone or not instance_name or not credentials_file_name:
                logger.error(f"Missing VM configuration: {vm}")
                continue
            
            credentials_file = os.path.join(CREDENTIALS_DIR, credentials_file_name)
            if not os.path.exists(credentials_file):
                logger.error(f"Credentials file {credentials_file} for GCP VM {instance_name} not found.")
                continue

            if gcp_handler.is_vm_terminated(project_id, zone, instance_name, credentials_file):
                logger.info(f"GCP VM {instance_name} is terminated. Starting it in 10 seconds...")
                time.sleep(10)  # Wait for 10 seconds before starting the VM
                if gcp_handler.start_vm(project_id, zone, instance_name, credentials_file):
                    logger.info(f"GCP VM {instance_name} started successfully.")
                else:
                    logger.error(f"Failed to start VM {instance_name}.")
            else:
                logger.info(f"GCP VM {instance_name} is already running.")

        # Azure VMs
        for vm in vms.get("azure", []):
            resource_group = vm.get("resource_group")
            instance_name = vm.get("instance_name")
            credentials_file_name = vm.get("credentials_file")

            if not resource_group or not instance_name or not credentials_file_name:
                logger.error(f"Missing VM configuration: {vm}")
                continue
            
            credentials_file = os.path.join(CREDENTIALS_DIR, credentials_file_name)
            if not os.path.exists(credentials_file):
                logger.error(f"Credentials file {credentials_file} for Azure VM {instance_name} not found.")
                continue

            if azure_handler.is_vm_terminated(resource_group, instance_name, credentials_file):
                logger.info(f"Azure VM {instance_name} is terminated. Starting it in 10 seconds...")
                time.sleep(10) # Wait for 10 seconds before starting the VM
                if azure_handler.start_vm(resource_group, instance_name, credentials_file):
                    logger.info(f"Azure VM {instance_name} started successfully.")
                else:
                    logger.error(f"Failed to start VM {instance_name}.")
            else:
                logger.info(f"Azure VM {instance_name} is either already running or manually stopped.")

        # TODO: Add AWS logic here

        # Sleep for a while before checking again
        logger.info(f"Sleeping for {SLEEP_DURATION} seconds before next check...")
        time.sleep(SLEEP_DURATION)

if __name__ == "__main__":
    main()
