import time
import json
from typing import Dict, List
from loguru import logger
import gcp

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
            credentials_file = vm.get("credentials_file")

            if not project_id or not zone or not instance_name or not credentials_file:
                logger.error(f"Missing VM configuration: {vm}")
                continue

            if gcp.is_vm_terminated(project_id, zone, instance_name, credentials_file):
                logger.info(f"GCP VM {instance_name} is terminated. Starting it in 10 seconds...")
                time.sleep(10)  # Wait for 10 seconds before starting the VM
                if gcp.start_vm(project_id, zone, instance_name, credentials_file):
                    logger.info(f"GCP VM {instance_name} started successfully.")
                else:
                    logger.error(f"Failed to start VM {instance_name}.")
            else:
                logger.info(f"GCP VM {instance_name} is already running.")

        # AWS VMs
        # Add AWS VM monitoring logic here

        # Azure VMs
        # Add Azure VM monitoring logic here

        # Add any other cloud provider monitoring logic here

        # Sleep for a while before checking again
        sleep_time = 300  # Check every 5 minutes
        logger.info(f"Sleeping for {sleep_time} seconds before next check...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
