---
applyTo: workspace/**
description: "Establish custom instructions for Azure deployments, including conventions, standards, proven practices, and supported deployment options."
---

# Azure Deployment Instructions

This file defines conventions, standards, proven practices, and supported deployment options for migrating the elevator dispatch simulation solution to Azure.

## Scope

Apply these instructions to Azure Infrastructure as Code, deployment automation, cloud resource configuration, and deployment-related documentation for the elevator dispatch system.

**When to use:** When writing or reviewing Bicep templates, Terraform modules, Azure CLI scripts, deployment prompts, Azure DevOps pipelines, or migration guidance.

**When NOT to use:** For local development (use `copilot-instructions.md`), Python/TypeScript source code (use language-specific instructions), or non-Azure cloud platforms.

---

## Architecture Principles

### 1. Keep It Simple and Containerized

- **Preferred pattern:** Containerize the FastAPI backend and UI into a single image, deploy to **Azure Container Apps** or **App Service (Linux containers)**.
- **Rationale:** Minimizes operational complexity, reuses the existing Docker Compose setup, and leverages existing devcontainer experience.
- **Alternative:** Deploy backend to **Azure Functions** only if the use case requires pure serverless with no persistent WebSocket needs.

### 2. Preserve Educational Value

- Keep the in-memory simulation engine as the default; do not mandate database persistence.
- Support optional PostgreSQL on **Azure Database for PostgreSQL** (single server or flexible server) for labs that add analytics or event logging.
- Avoid unnecessary services (no Redis cache, no Service Bus, no Application Insights unless explicitly requested).

### 3. Configuration-Driven Deployment

- Use environment variables and Azure Key Vault for secrets.
- Support toggling persistence (`DATABASE_URL` present → use Postgres; absent → in-memory).
- Keep deployment decisions in Infrastructure as Code, not baked into application code.

---

## Supported Deployment Options

### Option A: Azure Container Apps (Recommended)

**Target scenario:** Production-like, serverless container hosting with WebSocket support, auto-scaling, and minimal operational overhead.

**Deployment path:**
1. Build container image and push to **Azure Container Registry (ACR)**.
2. Create **Container App** environment (managed ingress, VNet integration optional).
3. Deploy container from ACR; bind to environment variables for DATABASE_URL, port (8080).
4. Optional: Add **Azure Database for PostgreSQL Flexible Server** and pass connection string via Key Vault reference.
5. Optional: Enable revision history and traffic splitting for canary deployments.

**IaC template:** Bicep or Terraform defining containerApp, containerRegistry, optional postgresqlFlexibleServer, and Key Vault for secrets.

**When to use:** When deploying to production, integrating with CI/CD pipelines, or supporting multiple environments (dev, staging, prod).

### Option B: Azure App Service (Linux Containers)

**Target scenario:** Simpler alternative to Container Apps; suitable for workshop or demo environments.

**Deployment path:**
1. Build container and push to ACR.
2. Create **App Service Plan** (Linux, Standard or Basic tier).
3. Deploy **App Service** from ACR; bind DATABASE_URL, WEBSITES_PORT=8080 as app settings.
4. Optional: Enable Application Insights for monitoring.
5. Optional: Configure deployment slots for staging/swap strategy.

**IaC template:** Bicep or Terraform defining appServicePlan, appService, optional appInsights, and containerRegistry.

**When to use:** When deploying to workshops, demo environments, or teams already familiar with App Service.

### Option C: Azure Container Instances (Dev/Test)

**Target scenario:** Quick testing or one-off deployments; not recommended for production or persistent workloads.

**Deployment path:**
1. Build and push image to ACR.
2. Create **Container Instance** from ACR, expose port 8080.
3. Pass DATABASE_URL as environment variable.

**IaC template:** Bicep template (containerInstance resource).

**When to use:** For testing before committing to Container Apps or App Service, or for ephemeral lab demonstrations.

### Option D: Azure Functions (Backend API Only)

**Target scenario:** If decoupling the UI from backend API and using serverless functions for REST endpoints only.

**Constraints:**
- WebSocket endpoint (`/ws`) will not work; requires Container Apps or App Service.
- Use **Static Web Apps** for the UI (HTML/CSS/JS from `workspace/ui/static/`).
- Adapt FastAPI routes to Azure Functions triggers (HTTP-triggered functions).

**When to use:** Only if the workshop explicitly requests a fully serverless architecture and can work without WebSocket live updates.

---

## Infrastructure as Code Standards

### Bicep Conventions

- Use `main.bicep` at repository root (`./infra/main.bicep`) or top-level (`./main.bicep`).
- Parameter file: `main.bicepparam` or environment-scoped (`prod.bicepparam`, `dev.bicepparam`).
- Define reusable modules in `infra/modules/` (e.g., `containerApp.bicep`, `containerRegistry.bicep`, `postgresql.bicep`).
- Use symbolic links or template references for shared modules across labs.
- Include outputs for resource IDs, connection strings, and endpoints needed by downstream tools.
- Document parameter constraints (allowed values, naming rules, regex patterns).

**Example structure:**
```
infra/
  main.bicep                 # Orchestrator
  main.bicepparam            # Default parameter values
  modules/
    containerApp.bicep       # Reusable container app definition
    containerRegistry.bicep  # ACR definition
    postgresql.bicep         # PostgreSQL Flexible Server definition
    keyvault.bicep           # Key Vault and secret provisioning
    networking.bicep         # VNet, subnet, NSG (optional)
```

### Terraform Conventions

- Use `main.tf` as orchestrator; split resources into `variables.tf`, `outputs.tf`, `locals.tf`.
- Define reusable modules in `modules/` (e.g., `modules/container_app/`, `modules/postgres/`).
- Use `terraform.tfvars` or `.auto.tfvars` for environment-specific values.
- Use `backend.tf` to configure state file location (Azure Storage Account or Terraform Cloud).
- Include validation rules and type constraints for variables.

**Example structure:**
```
terraform/
  main.tf
  variables.tf
  outputs.tf
  locals.tf
  terraform.tfvars
  backend.tf
  modules/
    container_app/
      main.tf
      variables.tf
      outputs.tf
    postgres/
      main.tf
      variables.tf
      outputs.tf
```

### Template Validation

- Run `bicep build --file main.bicep` to validate Bicep syntax.
- Run `terraform validate` and `terraform plan` to validate Terraform configuration before applying.
- Use Azure Resource Manager (ARM) template validation via CLI: `az deployment group validate --template-file main.bicep --resource-group rg-name`.
- Document expected output values (resource IDs, connection strings, endpoints).

---

## Naming Conventions

Follow Azure naming standards and organizational conventions:

| Resource Type | Pattern | Example |
| --- | --- | --- |
| Container Registry | `cr<project><env>` | `crelevatorprod` |
| Container App | `ca-<project>-<env>` | `ca-elevator-prod` |
| App Service | `app-<project>-<env>` | `app-elevator-prod` |
| App Service Plan | `plan-<project>-<env>` | `plan-elevator-prod` |
| Resource Group | `rg-<project>-<env>` | `rg-elevator-prod` |
| PostgreSQL Server | `psql-<project>-<env>` | `psql-elevator-prod` |
| Key Vault | `kv-<project>-<env>` | `kv-elevator-prod` |
| Storage Account | `st<project><env>` (no hyphens) | `stelephantprod` |
| Virtual Network | `vnet-<project>-<env>` | `vnet-elevator-prod` |

**Environment suffixes:** `dev`, `staging`, `prod` (lowercase).

**Region suffixes (optional):** Append region if multi-region support is needed, e.g., `ca-elevator-prod-eastus`.

---

## Configuration Management

### Environment Variables and Secrets

**Application-level (passed to container):**
- `FASTAPI_ENV`: `development`, `staging`, or `production` (defaults to `production`).
- `DATABASE_URL`: PostgreSQL connection string (optional; if absent, simulation runs in-memory).
  - Format: `postgresql+asyncpg://user:password@host:5432/database`
  - Use Azure Key Vault reference: `@Microsoft.KeyVault(SecretUri=https://kv-name.vault.azure.net/secrets/db-connection-string/)`
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR` (defaults to `INFO`).
- `ALLOWED_ORIGINS`: CORS allowed origins (defaults to `*` for local dev; restrict in production).

**Deployment-level (Bicep/Terraform parameters):**
- `location`: Azure region (e.g., `eastus`, `westeurope`).
- `environment`: `dev`, `staging`, or `prod`.
- `containerRegistryName`: Name of ACR registry.
- `containerImageTag`: Image tag or version.
- `databaseAdminUsername`: PostgreSQL admin user (store in Key Vault, do not hardcode).
- `databaseAdminPassword`: PostgreSQL admin password (reference from Key Vault).
- `appInsightsEnabled`: Boolean; enable Application Insights for monitoring.

### Secrets Management

- **Never commit secrets** to the repository.
- Use **Azure Key Vault** to store:
  - Database admin credentials.
  - API keys or connection strings for external services.
  - TLS certificates (optional, if required).
- Reference secrets in IaC templates using Key Vault resource IDs or reference functions:
  - Bicep: `@secure() parameters` or `reference(resourceId(...), ...).properties.value`
  - Terraform: `data.azurerm_key_vault_secret` or `azurerm_key_vault_secret`
- Use **managed identities** (user-assigned or system-assigned) for authentication instead of connection strings where possible.
- Rotate secrets periodically (quarterly minimum for production).

---

## Deployment Validation and Testing

### Pre-Deployment Checks

1. **Container image scan:**
   - Run `az acr run --registry <registry-name> --cmd 'acr build -t elevator:latest .'` to build and scan for vulnerabilities.
   - Review scan results; fail build if critical vulnerabilities are detected.

2. **IaC validation:**
   - Bicep: `bicep build main.bicep` (syntax check) + `az deployment group validate` (ARM template validation).
   - Terraform: `terraform validate` + `terraform plan` (resource planning and drift detection).

3. **Smoke tests:**
   - Curl health endpoint: `curl https://<app-endpoint>/api/state` (expect 200 JSON response).
   - Test WebSocket: Connect to `wss://<app-endpoint>/ws` and receive simulation updates.
   - Verify environment variables: Check container logs for configuration warnings.

### Post-Deployment Validation

1. **Endpoint availability:**
   - `GET https://<endpoint>/` returns HTML dashboard (200).
   - `GET https://<endpoint>/api/state` returns live JSON (200).
   - `WS wss://<endpoint>/ws` accepts WebSocket connections and streams updates.

2. **Database connectivity (if DATABASE_URL is set):**
   - Application logs show successful PostgreSQL connection.
   - Query `SELECT COUNT(*) FROM simulation_runs;` returns a count (0 or greater).

3. **Application logs:**
   - No startup errors or warnings.
   - Simulation ticks incrementing normally (check WebSocket stream or `/api/state` endpoint).
   - No unhandled exceptions in logs.

4. **Performance baseline:**
   - Response time for `/api/state` < 100ms.
   - WebSocket message delivery < 1 second per tick.
   - Container CPU/memory usage stable and under thresholds.

5. **Security baseline:**
   - No sensitive data (passwords, API keys) in container logs or environment.
   - CORS headers correctly restricted (if production).
   - HTTPS enforced (HTTP redirects to HTTPS).

---

## Proven Deployment Paths

### Path 1: Local → Docker Desktop → ACR → Container Apps (Recommended)

1. Develop and test locally with `python -m uvicorn api.server:app --reload`.
2. Build image with Docker Desktop: `docker build -t elevator:latest .`.
3. Test image locally: `docker run -p 8080:8080 elevator:latest`.
4. Log in to ACR: `az acr login --name <registry-name>`.
5. Tag and push: `docker tag elevator:latest <registry>.azurecr.io/elevator:latest && docker push <registry>.azurecr.io/elevator:latest`.
6. Deploy Bicep/Terraform to provision Container App and pull image from ACR.
7. Validate endpoints and logs.

**Duration:** 15–30 minutes per iteration.

### Path 2: Codespaces → Docker Daemon → ACR → Container Apps

1. Use `.devcontainer/docker-compose.yml` to run locally in Codespaces.
2. Build and push directly: `docker build -t <registry>.azurecr.io/elevator:latest . && docker push <registry>.azurecr.io/elevator:latest`.
3. Deploy IaC template (Bicep/Terraform) via `azd` or CLI.
4. Validate in Azure.

**Duration:** 10–25 minutes per iteration (faster than local Docker Desktop setup).

### Path 3: Azure DevOps Pipeline → ACR → Container Apps

1. Commit to repository.
2. Azure Pipelines automatically:
   - Runs tests (`python -m unittest discover`).
   - Builds container image.
   - Pushes to ACR.
   - Deploys IaC template to Azure.
   - Runs smoke tests.
3. Manual approval gates before prod deployment.

**Duration:** 5–15 minutes (fully automated).

---

## Database Migration Strategy

### From In-Memory to PostgreSQL

1. **Assessment phase:**
   - Determine which data should persist (simulation runs, passenger events, scenario seeds).
   - Design schema (tables, indexes, retention policies).
   - Estimate storage requirements (typically < 1 GB per month for workshop-scale simulation).

2. **Schema deployment:**
   - Use migration scripts in `.devcontainer/postgres-init/` as a starting point.
   - Add version-tracked migrations (Alembic or custom SQL migration directory).
   - Test schema on local Postgres sidecar first.

3. **Application changes:**
   - Update `workspace/api/server.py` to write events to PostgreSQL (via SQLAlchemy async engine).
   - Retain in-memory simulation engine (do not persist intermediate tick state).
   - Use connection pool (asyncpg) to manage concurrent connections.

4. **Deployment:**
   - Provision **Azure Database for PostgreSQL Flexible Server** via Bicep/Terraform.
   - Store connection string in Azure Key Vault.
   - Reference connection string in Container App environment variables.
   - Test application against Azure Postgres before cutover.

5. **Rollback plan:**
   - Keep in-memory mode as fallback if database is unavailable.
   - Log errors but do not crash the simulator if database writes fail.

### Azure PostgreSQL Options

| Option | Tier | Suitable For | Cost |
| --- | --- | --- | --- |
| **Flexible Server** | Single or HA (2 standbys) | Production workloads | $30–200/month |
| **Single Server** | Standalone (deprecated) | Workshops, dev/test | $15–100/month |
| **Azure Cosmos DB (PostgreSQL)** | Distributed | Multi-tenant, high concurrency | $60+/month |

**Recommendation:** Use **Flexible Server** single-node for production; **Single Server** for labs (if still available); development uses local Docker Postgres.

---

## Monitoring and Observability

### Application Insights (Optional)

- Add `azure-monitor-opentelemetry` package to Python dependencies if monitoring is required.
- Configure tracing in `workspace/api/server.py` to export traces and metrics.
- Use Application Insights to monitor response times, error rates, dependency health.
- Set alerts for > 1% error rate or response time > 500ms.

### Container App Observers

- Built-in: CPU, memory, request count, response time (via Azure Portal or CLI).
- Logs: Stream container logs via `az containerapp logs show --resource-group <rg> --name <app-name>`.
- Revisions: Track deployment history and traffic split between versions.

### Log Aggregation (Optional)

- Use **Log Analytics Workspace** with Application Insights for centralized log querying.
- Query examples:
  - `AppTraces | where Message contains "error" | summarize count() by TimeGenerated`
  - `AppRequests | summarize avg(DurationMs), max(DurationMs) by Name`

---

## Cost Optimization

### Keep Costs Low

1. **Use App Service Free tier** for single-instance dev/test deployments (limited to 1 GB RAM).
2. **Use Container Apps consumption plan** (pay per request) instead of always-on containers.
3. **Avoid managed databases** unless persistence is required; use local Docker Postgres for dev/test.
4. **Single-node PostgreSQL Flexible Server** (not HA) for non-production; HA adds ~$15–30/month.
5. **No caching, CDN, or Application Insights** unless explicitly needed.
6. **Cleanup:** Delete resource groups and Azure resources when labs are complete.

### Estimated Monthly Costs (Production Baseline)

| Component | Cost | Notes |
| --- | --- | --- |
| Container Apps (2 vCPU, 4 GB RAM) | $50–80 | Consumption plan; scales with request volume |
| PostgreSQL Flexible Server (single-node) | $30–50 | 1–2 vCPU, 10 GB storage |
| Container Registry (Standard) | $10–25 | Storage + pull operations |
| Key Vault | $0.60–1.00 | 10K operations included |
| **Total** | **$90–155/month** | Scales with usage |

---

## Supported Deployment Checklist

- [ ] **Bicep template** created and validated (`bicep build`).
- [ ] **Container image** built locally and pushed to ACR.
- [ ] **Container App** (or App Service) provisioned and pulls image from ACR.
- [ ] **Health endpoint** responsive (`GET /api/state` → 200).
- [ ] **WebSocket endpoint** accepts connections (`WS /ws`).
- [ ] **Application logs** show clean startup and normal tick progression.
- [ ] **Environment variables** validated (DATABASE_URL, FASTAPI_ENV, etc.).
- [ ] **Database connectivity** tested (if DATABASE_URL is set).
- [ ] **CORS headers** correctly configured for production.
- [ ] **DNS/CNAME** configured (if custom domain is needed).
- [ ] **TLS certificate** valid and auto-renewal enabled (Container Apps/App Service handles this).
- [ ] **Smoke tests** passed (health checks, endpoint validation, performance).
- [ ] **Resource Group** properly tagged and documented.
- [ ] **Secrets** stored in Key Vault (no hardcoded passwords).
- [ ] **Cost estimate** reviewed and approved.

---

## Next Steps for a New Deployment

1. **Choose deployment option** (Container Apps recommended).
2. **Create Bicep template** (or Terraform module) using the structure in `infra/main.bicep`.
3. **Build container image** locally and test.
4. **Push to ACR** and validate pull.
5. **Deploy IaC template** and validate endpoints.
6. **Run smoke tests** and monitor logs.
7. **Document deployment steps** in a Copilot prompt (e.g., `.github/prompts/04.00.migrate-solution-to-azure.prompt.md`).

---

## References

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure App Service Documentation](https://learn.microsoft.com/en-us/azure/app-service/)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Best Practices for Container Deployments](https://learn.microsoft.com/en-us/azure/container-apps/best-practices)
- [Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/azure/postgresql/)
- [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/)
