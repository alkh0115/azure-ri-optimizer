# Azure RI & Savings Plan Optimizer

This project is a **cost optimization solution** designed for large Azure environments. It automatically generates a monthly report identifying underutilized Reserved Instances (RIs) and Savings Plans (SPs), uploads the report to Blob Storage, and sends it via email using a Logic App.

---

## Project Structure

```
azure-ri-optimizer/
├── .vscode/                         # VSCode settings for development
│   ├── extensions.json
│   └── settings.json
├── function_app.py                 # Main function app with timer trigger
├── ri_optimizer.py                 # Core logic for generating RI/SP report and uploading
├── requirements.txt                # Python dependencies
├── host.json                       # Azure Function host configuration
├── local.settings.json             # Local secrets (excluded from Git)
├── .funcignore
├── .gitignore
├── README.md                                            
```

---

## Features

- Fetches Azure RI/SP utilization using REST APIs and CLI.
- Identifies underutilized assets (<70% usage).
- Exports a detailed CSV report.
- Uploads report to Azure Blob Storage.
- Automatically sends the report via email using Logic App.

---

## Prerequisites

- Azure Subscription (e.g., Azure for Students)
- Python 3.11 installed
- [Azure CLI installed and signed in](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- Azure Functions Core Tools
- Storage account and container named `reports`

---

## Steps to Run Locally

### 1. Clone the Repo and Setup Environment
```bash
cd azure-ri-optimizer
python -m venv .venv
.venv\Scripts\activate   # On Windows
pip install -r requirements.txt
```

### 2. Set Environment Variables (in `local.settings.json`)
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<your_connection_string>",
    "AZURE_STORAGE_CONNECTION_STRING": "<your_connection_string>",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

### 3. Run the Azure Function Locally
```bash
func start
```

This will:
- Trigger the function on startup.
- Generate a CSV file like `ri_sp_report_YYYYMMDD.csv`
- Upload it to your Blob Storage container

---

## Deploy Function to Azure

### 1. Create Resource Group & Storage Account
```bash
az group create --name ri-funcapp-rg --location canadacentral
az storage account create \
  --name rifuncappstorage0115 \
  --location canadacentral \
  --resource-group ri-funcapp-rg \
  --sku Standard_LRS
```

### 2. Deploy the Function App
```bash
az functionapp create \
  --resource-group ri-funcapp-rg \
  --consumption-plan-location canadacentral \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux \
  --name rioptimizer0115 \
  --storage-account rifuncappstorage0115
```

### 3. Configure App Settings
```bash
az functionapp config appsettings set \
  --name rioptimizer0115 \
  --resource-group ri-funcapp-rg \
  --settings \
  "AZURE_STORAGE_CONNECTION_STRING=<connection_string>"
```

---

## ❌ Blocked: Azure AD App Registration

- We attempted to create a Service Principal with:
```bash
az ad sp create-for-rbac --name "RITrackerApp" --role Reader --scopes /subscriptions/<your-subscription-id>
```
- ❗ This failed due to lack of directory permission.
- ✅ Currently using local `az account get-access-token` workaround.

---

## Logic App for Email Notifications

1. Create a new **Consumption Logic App** in Azure.
2. Use **"When a blob is added or modified (properties only)"** trigger.
3. Connect to your storage account and container (`reports`).
4. Add **Get Blob Content** action.
5. Add **Send Email (Gmail or Outlook)** action:
   - To: your email
   - Subject: "RI/SP Report Available"
   - Body: Summary text
   - Attach the blob content using dynamic fields

If email lands in junk folder, mark it as safe.

---

## Clean-up Resources

To avoid Azure credit charges:
```bash
az group delete --name ri-funcapp-rg --no-wait --yes
```
Or delete manually from the Azure Portal.

---

## Final Output
- 📄 CSV report of underutilized RIs and SPs
- ☁️ Stored in Azure Blob Storage
- 📧 Automatically emailed via Logic App

---

