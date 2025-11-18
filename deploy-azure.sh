#!/bin/bash

# ============================================================================
# AlphaLLM-API - Azure Deployment Script
# 🇫🇷 Région: francecentral (Paris)
# ============================================================================

set -e  # Exit on error

# Parse command line arguments
SKIP_RESOURCE_GROUP=false
SKIP_STORAGE=false
SKIP_APP_PLAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-rg) SKIP_RESOURCE_GROUP=true; shift ;;
        --skip-storage) SKIP_STORAGE=true; shift ;;
        --skip-plan) SKIP_APP_PLAN=true; shift ;;
        --skip-all) SKIP_RESOURCE_GROUP=true; SKIP_STORAGE=true; SKIP_APP_PLAN=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# CONFIGURATION
# ============================================================================

# Variables
RESOURCE_GROUP="AlphaLLM-RG"
LOCATION="francecentral"  # 🇫🇷 Région: France (Paris)
APP_NAME="alphallm-api"
STORAGE_ACCOUNT="alphallmstorage"
SUBSCRIPTION_ID=""
TENANT_ID=""

# Settings
DATA_SERVICE_BASE_URL="http://de5.azurhosts.com:25692/"
FUNCTIONS_WORKER_RUNTIME="python"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed"
        exit 1
    fi
    print_success "$1 is installed"
}

# ============================================================================
# PRE-DEPLOYMENT CHECKS
# ============================================================================

print_header "PRE-DEPLOYMENT CHECKS"

check_command az
check_command git
check_command python3

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure"
    echo "Run: az login"
    exit 1
fi

print_success "Logged in to Azure"

# Get current subscription
CURRENT_SUB=$(az account show --query id -o tsv)
print_info "Current subscription: $CURRENT_SUB"

echo ""
echo "Usage options:"
echo "  ./deploy-azure.sh                    # Full deployment"
echo "  ./deploy-azure.sh --skip-rg          # Skip resource group"
echo "  ./deploy-azure.sh --skip-storage     # Skip storage account"
echo "  ./deploy-azure.sh --skip-plan        # Skip app service plan"
echo "  ./deploy-azure.sh --skip-all         # Skip RG, storage, and plan"
echo ""

# ============================================================================
# INPUT: Subscription ID & Tenant ID
# ============================================================================

print_header "AZURE CREDENTIALS"

if [ -z "$SUBSCRIPTION_ID" ]; then
    read -p "Enter SUBSCRIPTION_ID (or press Enter to use current: $CURRENT_SUB): " input_sub
    SUBSCRIPTION_ID="${input_sub:-$CURRENT_SUB}"
fi

if [ -z "$TENANT_ID" ]; then
    CURRENT_TENANT=$(az account show --query tenantId -o tsv)
    read -p "Enter TENANT_ID (or press Enter to use current: $CURRENT_TENANT): " input_tenant
    TENANT_ID="${input_tenant:-$CURRENT_TENANT}"
fi

print_success "SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
print_success "TENANT_ID: $TENANT_ID"

# ============================================================================
# 1. CREATE RESOURCE GROUP
# ============================================================================

if [ "$SKIP_RESOURCE_GROUP" = true ]; then
    print_warning "SKIPPING: Resource Group creation (use --skip-rg to skip)"
    echo ""
else
    print_header "STEP 1: Creating Resource Group"

    if az group exists --name "$RESOURCE_GROUP" | grep -q true; then
        print_warning "Resource Group '$RESOURCE_GROUP' already exists"
    else
        print_info "Creating resource group: $RESOURCE_GROUP (Location: $LOCATION)"
        az group create \
            --name "$RESOURCE_GROUP" \
            --location "$LOCATION"
        print_success "Resource group created"
    fi
fi

# ============================================================================
# 2. CREATE STORAGE ACCOUNT
# ============================================================================

if [ "$SKIP_STORAGE" = true ]; then
    print_warning "SKIPPING: Storage Account creation (use --skip-storage to skip)"
    echo ""
else
    print_header "STEP 2: Creating Storage Account"

    if az storage account exists \
        --name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        print_warning "Storage account '$STORAGE_ACCOUNT' already exists"
    else
        print_info "Creating storage account: $STORAGE_ACCOUNT"
        az storage account create \
            --name "$STORAGE_ACCOUNT" \
            --resource-group "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --sku Standard_LRS
        print_success "Storage account created"
        print_info "Waiting for storage account to be available (30 seconds)..."
        sleep 30
    fi

    # Get storage connection string
    STORAGE_CONNECTION=$(az storage account show-connection-string \
        --name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --query connectionString -o tsv)

    print_success "Storage connection string retrieved"
fi

# ============================================================================
# 3. CREATE APP SERVICE PLAN
# ============================================================================

if [ "$SKIP_APP_PLAN" = true ]; then
    print_warning "SKIPPING: App Service Plan creation (use --skip-plan to skip)"
    echo ""
else
    print_header "STEP 3: Creating App Service Plan"

    APP_PLAN="${APP_NAME}-plan"

    if az appservice plan show \
        --name "$APP_PLAN" \
        --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        print_warning "App Service Plan '$APP_PLAN' already exists"
    else
        print_info "Creating app service plan: $APP_PLAN (Location: $LOCATION)"
        az appservice plan create \
            --name "$APP_PLAN" \
            --resource-group "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --sku B1 \
            --is-linux
        print_success "App Service Plan created"
        print_info "Waiting for plan to be available (30 seconds)..."
        sleep 30
    fi
fi

# ============================================================================
# 4. CREATE FUNCTION APP
# ============================================================================

print_header "STEP 4: Creating Function App"

APP_PLAN="${APP_NAME}-plan"

# Vérifier que le plan existe
if ! az appservice plan show \
    --name "$APP_PLAN" \
    --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_warning "App Service Plan '$APP_PLAN' not found. Creating it now..."
    az appservice plan create \
        --name "$APP_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku B1 \
        --is-linux
    print_success "App Service Plan created"
    print_info "Waiting for plan to be fully available (60 seconds)..."
    sleep 60
fi

if az functionapp show \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_warning "Function App '$APP_NAME' already exists"
else
    print_info "Creating function app: $APP_NAME"
    az functionapp create \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --storage-account "$STORAGE_ACCOUNT" \
        --plan "$APP_PLAN" \
        --runtime python \
        --runtime-version 3.12 \
        --functions-version 4
    print_success "Function app created"
    print_info "Waiting for function app to be fully available (60 seconds)..."
    sleep 60
fi

# ============================================================================
# 5. CONFIGURE APPLICATION SETTINGS
# ============================================================================

print_header "STEP 5: Configuring Application Settings"

print_info "Setting environment variables..."
az functionapp config appsettings set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        DATA_SERVICE_BASE_URL="$DATA_SERVICE_BASE_URL" \
        FUNCTIONS_WORKER_RUNTIME="$FUNCTIONS_WORKER_RUNTIME"

print_success "Application settings configured"

# ============================================================================
# 6. CREATE SERVICE PRINCIPAL (for GitHub Actions)
# ============================================================================

print_header "STEP 6: Creating Service Principal for GitHub Actions"

SERVICE_PRINCIPAL_NAME="github-actions-${APP_NAME}"

# Create app registration
print_info "Creating app registration: $SERVICE_PRINCIPAL_NAME"
APP_REG=$(az ad app create --display-name "$SERVICE_PRINCIPAL_NAME" --query appId -o tsv 2>/dev/null || echo "")

if [ -z "$APP_REG" ]; then
    # Try to get existing
    APP_REG=$(az ad app list --display-name "$SERVICE_PRINCIPAL_NAME" --query "[0].appId" -o tsv 2>/dev/null || echo "")
fi

if [ -z "$APP_REG" ]; then
    print_error "Could not create or find app registration"
    exit 1
fi

print_success "App registration created: $APP_REG"

# Create service principal from app registration
SP_ID=$(az ad sp create --id "$APP_REG" --query id -o tsv 2>/dev/null || echo "")

if [ -z "$SP_ID" ]; then
    # Try to get existing
    SP_ID=$(az ad sp list --display-name "$SERVICE_PRINCIPAL_NAME" --query "[0].id" -o tsv 2>/dev/null || echo "")
fi

if [ -z "$SP_ID" ]; then
    print_error "Could not create or find service principal"
    exit 1
fi

print_success "Service principal created: $SP_ID"

# Assign Contributor role to the service principal
print_info "Assigning Contributor role to service principal..."
az role assignment create \
    --assignee "$SP_ID" \
    --role "Contributor" \
    --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" 2>/dev/null || {
    print_warning "Role assignment might already exist"
}

print_success "Contributor role assigned"

# Create client secret
print_info "Creating client secret (valid for 1 year)..."
CLIENT_SECRET=$(az ad app credential create \
    --id "$APP_REG" \
    --display-name "github-actions-secret" \
    --query password -o tsv)

if [ -z "$CLIENT_SECRET" ]; then
    print_error "Could not create client secret"
    exit 1
fi

print_success "Client secret created"

# ============================================================================
# 7. DISPLAY GITHUB SECRETS
# ============================================================================

print_header "STEP 7: GitHub Secrets Configuration"

echo ""
echo "🔐 Add these secrets to your GitHub repository:"
echo "   Repository → Settings → Secrets and variables → Actions → New repository secret"
echo ""
echo "Secret name: AZURE_CLIENT_ID"
echo "Value: $CLIENT_ID"
echo ""
echo "Secret name: AZURE_TENANT_ID"
echo "Value: $TENANT_ID"
echo ""
echo "Secret name: AZURE_SUBSCRIPTION_ID"
echo "Value: $SUBSCRIPTION_ID"
echo ""

# ============================================================================
# 8. SAVE CONFIGURATION
# ============================================================================

print_header "STEP 8: Saving Configuration"

CONFIG_FILE="azure-deployment-config.env"

cat > "$CONFIG_FILE" << EOF
#!/bin/bash
# Azure Deployment Configuration
# Generated: $(date)
# 🇫🇷 Région: francecentral (Paris)

export RESOURCE_GROUP="$RESOURCE_GROUP"
export LOCATION="$LOCATION"
export APP_NAME="$APP_NAME"
export STORAGE_ACCOUNT="$STORAGE_ACCOUNT"
export SUBSCRIPTION_ID="$SUBSCRIPTION_ID"
export TENANT_ID="$TENANT_ID"
export CLIENT_ID="$CLIENT_ID"

# Data Service
export DATA_SERVICE_BASE_URL="$DATA_SERVICE_BASE_URL"

# Connection Strings (Local use only - DO NOT COMMIT)
export AzureWebJobsStorage="$STORAGE_CONNECTION"
EOF

print_success "Configuration saved to: $CONFIG_FILE"
print_warning "⚠️  DO NOT COMMIT THIS FILE - It contains secrets!"

# ============================================================================
# 9. DEPLOYMENT VERIFICATION
# ============================================================================

print_header "STEP 9: Verifying Deployment"

# Verify Function App
if az functionapp show \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    print_success "Function App verified"
else
    print_error "Function App not found"
    exit 1
fi

# Get Function App URL
FUNCTION_URL=$(az functionapp show \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query defaultHostName -o tsv)

print_success "Function App URL: https://$FUNCTION_URL"

# ============================================================================
# 10. NEXT STEPS
# ============================================================================

print_header "NEXT STEPS"

echo ""
echo "✅ Azure resources created successfully!"
echo ""
echo "1️⃣  Add GitHub Secrets (see output above)"
echo "   → Go to GitHub → Settings → Secrets and variables → Actions"
echo "   → Add 3 secrets: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID"
echo ""
echo "2️⃣  Push to 'prod' branch to trigger GitHub Actions"
echo "   git push origin main:prod"
echo ""
echo "3️⃣  Monitor deployment"
echo "   → GitHub → Actions → Check latest workflow run"
echo ""
echo "4️⃣  Test your API"
echo "   curl https://$FUNCTION_URL/api/info"
echo ""
echo "5️⃣  View logs in Azure Portal"
echo "   → Function App → Application Insights → Logs"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

print_header "DEPLOYMENT SUMMARY"

echo ""
echo "📍 Location: $LOCATION (🇫🇷 France - Paris)"
echo "📦 Resource Group: $RESOURCE_GROUP"
echo "📋 App Service Plan: $APP_PLAN"
echo "🚀 Function App: $APP_NAME"
echo "💾 Storage Account: $STORAGE_ACCOUNT"
echo "🔗 URL: https://$FUNCTION_URL"
echo ""
echo "✨ Configuration saved to: $CONFIG_FILE"
echo ""
