provider "azurerm" {
  features {
    
  }
  subscription_id = var.subscription_id
  tenant_id = var.tenant_id
  client_id = var.client_id
}

resource "azurerm_resource_group" "weekly_meeting_agenda_resources" {
  name     = var.resource_group_name
  location = "East US"
}

resource "azurerm_storage_account" "weekly_meeting_agenda_storage_account" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.weekly_meeting_agenda_resources.name
  location                 = azurerm_resource_group.weekly_meeting_agenda_resources.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_service_plan" "weekly_meeting_agenda_plan" {
  name                     = var.service_plan_name
  resource_group_name      = azurerm_resource_group.weekly_meeting_agenda_resources.name
  location                 = azurerm_resource_group.weekly_meeting_agenda_resources.location
  os_type                  = "Linux"
  sku_name                 = "B2"
}

resource "azurerm_linux_function_app" "weekly_meeting_agenda_app" {
  name                       = var.function_app_name
  resource_group_name        = azurerm_resource_group.weekly_meeting_agenda_resources.name
  location                   = azurerm_resource_group.weekly_meeting_agenda_resources.location

  storage_account_name       = azurerm_storage_account.weekly_meeting_agenda_storage_account.name
  storage_account_access_key = azurerm_storage_account.weekly_meeting_agenda_storage_account.primary_access_key
  service_plan_id            = azurerm_service_plan.weekly_meeting_agenda_plan.id

  site_config { 
    application_stack {
      python_version          = "3.10"
    }
  }

  auth_settings {
    enabled                       = true
    default_provider              = "AzureActiveDirectory"
    active_directory {
      client_id     = var.client_id
      client_secret = var.client_secret
      allowed_audiences = [
        "api://${var.client_id}" 
      ]
    }

    token_store_enabled           = true
    runtime_version               = "~1"
    unauthenticated_client_action = "RedirectToLoginPage"
    issuer                        = "https://sts.windows.net/${var.tenant_id}/"  # Replace with your Directory (tenant) ID
    allowed_external_redirect_urls = [
      "https://${var.function_app_name}.azurewebsites.net/api/notify"  # Replace with your Function App URL
    ]
  }

}