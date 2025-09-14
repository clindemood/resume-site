# Resume Site

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

The application will be available at <http://localhost:8000/>.

## Deploying to Azure

1. Log in to Azure and create a resource group (replace names as needed):
   ```bash
   az login
   az group create --name resume-rg --location eastus
   ```
2. Build the Docker image locally:
   ```bash
   docker build -t resume-site:latest .
   ```
3. Create an Azure Container Registry and push the image:
   ```bash
   ACR_NAME=myregistry
   az acr create --resource-group resume-rg --name $ACR_NAME --sku Basic
   az acr login --name $ACR_NAME
   docker tag resume-site:latest $ACR_NAME.azurecr.io/resume-site:latest
   docker push $ACR_NAME.azurecr.io/resume-site:latest
   ```
4. Provision an App Service plan and deploy the container image to a Web App:
   ```bash
   az appservice plan create --name resume-plan --resource-group resume-rg --is-linux --sku B1
   az webapp create --name resume-app --resource-group resume-rg --plan resume-plan \
     --deployment-container-image-name $ACR_NAME.azurecr.io/resume-site:latest
   ```

