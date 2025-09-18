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
az group create --name resume-site-rg --location <azure-region>
```

## 4. Create an App Service plan

```bash
az appservice plan create --name resume-site-plan --resource-group resume-site-rg --sku B1 --is-linux
```

`B1` is a basic tier that incurs a small cost; adjust the SKU as needed.

## 5. Create the web app

```bash
az webapp create --resource-group resume-site-rg --plan resume-site-plan --name <unique-app-name> --runtime "PYTHON:3.11"
```

Choose a globally unique name; the site will be available at
`https://<unique-app-name>.azurewebsites.net`.

## 6. Set the startup command

App Service expects a command that starts the application. Use Uvicorn to run
the FastAPI app:

```bash
az webapp config set --resource-group resume-site-rg --name <unique-app-name> --startup-file "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

This command uses the `PORT` environment variable provided by App Service to
choose the correct port. Add any required environment variables with
`az webapp config appsettings set`.

## 7. Enable build during deployment

Azure installs dependencies from `requirements.txt` during an Oryx build. If
that build step is skipped, packages such as Uvicorn never get installed. Turn
on build-on-deploy for the site (you only need to run this once per app):

```bash
az webapp config appsettings set --resource-group resume-site-rg --name <unique-app-name> --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

Make sure `requirements.txt` lives in the root of the deployed folder so the
build step can find it.

## 8. Deploy the code

Deploy the current directory to the new web app using zip deployment. Adding
`--build-remote true` forces Azure to run an Oryx build during this push, which
generates the manifest and installs dependencies from `requirements.txt`:

```bash
az webapp deploy --resource-group resume-site-rg --name <unique-app-name> --src-path . --type zip --build-remote true
```

The CLI zips the source and uploads it to the service. With build-on-deploy
enabled, App Service installs dependencies from `requirements.txt` and starts
the process using the startup command.

## 9. Browse the site

Once deployment finishes, open your browser to:

```
https://<unique-app-name>.azurewebsites.net/
```

You should see the interactive resume interface.

## 10. Optional enhancements

- **Redis session store**: Provision an [Azure Cache for Redis](https://learn.microsoft.com/azure/azure-cache-for-redis/overview) instance and
  set the `SESSION_REDIS_URL` app setting to enable shared session storage.
- **Custom domain & HTTPS**: Use `az webapp config hostname add` to map a custom
  domain and enable managed certificates.
- **Continuous deployment**: Create a GitHub Actions workflow that runs tests
  and uses `azure/webapps-deploy` to push on every commit.

## Troubleshooting

- **`uvicorn: not found` in the container logs** – The deployment skipped the
  build step, so dependencies were never installed. Confirm that
  `SCM_DO_BUILD_DURING_DEPLOYMENT` is `true`, redeploy with `--build-remote
  true`, and make sure `requirements.txt` lives in the root of the deployed
  folder.
- **App settings changed but nothing updates** – Toggling build flags or startup
  commands does not rebuild past deployments. Run another `az webapp deploy`
  after changing settings so Oryx can produce a fresh manifest.
- **Verify what made it to Azure** – Open an SSH session and inspect the
  directory to ensure `app/` and `requirements.txt` are present:

  ```bash
  az webapp ssh --resource-group resume-site-rg --name <unique-app-name>
  ```

  Once connected, run:

  ```bash
  ls -al /home/site/wwwroot
  ```

## Cleanup

To remove all resources when finished:

```bash
az group delete --name resume-site-rg
```

