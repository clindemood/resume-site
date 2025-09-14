# Deploying to Azure

This guide explains how to run the FastAPI resume site on [Microsoft Azure](https://azure.microsoft.com/).
The steps below use the Azure CLI and Azure App Service for Linux. The same
approach works for personal or professional deployments.

## Prerequisites

- An Azure subscription.
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed locally.
- Python 3.11+ and Git.
- (Optional) A Redis instance if you want to enable session storage via `SESSION_REDIS_URL`.

## 1. Clone the project

```bash
git clone https://github.com/<your-user>/resume-site.git
cd resume-site
```

## 2. Log in to Azure

```bash
az login
```
Follow the browser prompts to authenticate.

## 3. Create a resource group

```bash
az group create \
  --name resume-site-rg \
  --location <azure-region>
```

## 4. Create an App Service plan

```bash
az appservice plan create \
  --name resume-site-plan \
  --resource-group resume-site-rg \
  --sku B1 \
  --is-linux
```

`B1` is a basic tier that incurs a small cost; adjust the SKU as needed.

## 5. Create the web app

```bash
az webapp create \
  --resource-group resume-site-rg \
  --plan resume-site-plan \
  --name <unique-app-name> \
  --runtime "PYTHON:3.11"
```

Choose a globally unique name; the site will be available at
`https://<unique-app-name>.azurewebsites.net`.

## 6. Set the startup command

App Service expects a command that starts the application. Use Uvicorn to run
the FastAPI app:

```bash
az webapp config set \
  --resource-group resume-site-rg \
  --name <unique-app-name> \
  --startup-file "uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

Add any required environment variables with `az webapp config appsettings set`.

## 7. Deploy the code

Deploy the current directory to the new web app using zip deployment:

```bash
az webapp deploy \
  --resource-group resume-site-rg \
  --name <unique-app-name> \
  --src-path .
```

The CLI zips the source and uploads it to the service. App Service installs
dependencies from `requirements.txt` and starts the process using the startup
command.

## 8. Browse the site

Once deployment finishes, open your browser to:

```
https://<unique-app-name>.azurewebsites.net/
```

You should see the interactive resume interface.

## 9. Optional enhancements

- **Redis session store**: Provision an [Azure Cache for Redis](https://learn.microsoft.com/azure/azure-cache-for-redis/overview) instance and
  set the `SESSION_REDIS_URL` app setting to enable shared session storage.
- **Custom domain & HTTPS**: Use `az webapp config hostname add` to map a custom
  domain and enable managed certificates.
- **Continuous deployment**: Create a GitHub Actions workflow that runs tests
  and uses `azure/webapps-deploy` to push on every commit.

## Cleanup

To remove all resources when finished:

```bash
az group delete --name resume-site-rg
```

