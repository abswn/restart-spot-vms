# restart-spot-vms

An automation tool to restart stopped (deallocated) spot VMs across multiple cloud providers (AWS, Azure, GCP). Currently, it supports only **GCP** spot VMs.

## GCP Setup: Creating a Service Account

### Steps:

1. **Go to the Google Cloud Console**  
   [https://console.cloud.google.com/](https://console.cloud.google.com/)

2. **Select your project**  
   Use the project selector at the top of the page to choose your GCP project.

3. **Navigate to Service Accounts**  
   In the left sidebar, go to **IAM & Admin > Service Accounts**.

4. **Create a new service account**  
   - Click **Create Service Account**.
   - Enter a name and description.
   - Click **Create and Continue**.

5. **Grant the required role**  
   - In the "Grant this service account access to project" step, add the role:  
     **Compute Instance Admin (v1)** (`roles/compute.instanceAdmin.v1`)
   - Click **Continue** and then **Done**.

6. **Create and download a key**  
   - Click on the service account you just created.
   - Go to the **Keys** tab.
   - Click **Add Key > Create new key**.
   - Select **JSON** and click **Create**.
   - A `.json` file will be downloaded to your computer.

7. **Use the credentials**  
   - Place the downloaded JSON file in the `credentials` directory (e.g., `credentials/credentials.json`).
   - Reference it in the `vms.json` configuration for each GCP VM:
     ```json
     "credentials_file": "credentials.json"
     ```

**Note:**  
A service account is created within a specific GCP project and its permissions apply only to resources in that project.  
If you want to manage VMs across multiple GCP projects, you can either:
- Create a service account in each project, or
- Grant an existing service account access to additional projects by assigning it the necessary roles in those projects.

## Azure Setup: Creating an Application and Getting Credentials

### Steps:

1. **Go to the Azure Portal**  
   [https://portal.azure.com/](https://portal.azure.com/)

2. **Register a new application**  
   - Navigate to **Azure Active Directory > App registrations**.
   - Click **New registration**.
   - Enter a name and register the application.

3. **Create a client secret**  
   - In app registration, go to **Certificates & secrets**.
   - Click **New client secret**, add a description, and set an expiry.
   - Copy the generated value (you won't see it again).

4. **Get tenant and client IDs**  
   - In app registration, copy the **Application (client) ID** and **Directory (tenant) ID**.

5. **Assign a role to the application**  
   - Go to **Subscription** or **Resource Group** where your VMs are.
   - Click **Access control (IAM) > Add > Add role assignment**.
   - Assign the role **Virtual Machine Contributor** to the application (search for the app by name).

6. **Get your subscription ID**  
   - Go to **Subscriptions** in the portal and copy the **Subscription ID**.

7. **Create a credentials JSON file**  
   Create a file (e.g., `azure_credentials.json`) in the `credentials` directory with the following content:
   ```json
   {
     "AZURE_CLIENT_ID": "<your-client-id>",
     "AZURE_CLIENT_SECRET": "<your-client-secret>",
     "AZURE_TENANT_ID": "<your-tenant-id>",
     "AZURE_SUBSCRIPTION_ID": "<your-subscription-id>"
   }
   ```

8. **Reference the credentials in your `vms.json`**  
   ```json
   "credentials_file": "azure_credentials.json"
   ```

## Configuration Example (`vms.json`)

```json
{
  "gcp": [
    {
      "project_id": "your-gcp-project",
      "zone": "us-central1-a",
      "instance_name": "my-gcp-vm",
      "credentials_file": "credentials.json",
      "description": "This is a GCP spot VM for testing"
    }
  ],
  "azure": [
    {
      "resource_group": "myResourceGroup",
      "instance_name": "myAzureVM",
      "credentials_file": "azure_credentials.json",
      "description": "Azure spot VM for testing"
    }
  ]
}
```

## Usage

1. Create `vms.json`
2. Place the credential files in `credentials` directory.
3. Run the script:
   ```sh
   sudo apt install python3-venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python3 main.py
   ```

## Security Reminder
Keep the GCP and Azure credentials file secure. Anyone with this file can access the cloud accounts according to the permissions granted.

## License

MIT License
