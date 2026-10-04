# Resource group
resource "azurerm_resource_group" "rg" {
    name = "${var.prefix}-rg"
    location = var.location
}

# Network
resource "azurerm_virtual_network" "vnet" {
    name = "${var.prefix}-vnet"
    resource_group_name = azurerm_resource_group.rg.name
    location = azurerm_resource_group.rg.location
    address_space = ["10.60.0.0/16"]
}

# Subnet
resource "azurerm_subnet" "api" {
    name = "api"
    resource_group_name = azurerm_resource_group.rg.name
    virtual_network_name = azurerm_virtual_network.vnet.name
    address_prefixes = ["10.60.1.0/24"]
    default_outbound_access_enabled = false
}

# Security Rules
resource "azurerm_network_security_group" "api" {
    name = "${var.prefix}-api-nsg"
    resource_group_name = azurerm_resource_group.rg.name
    location = azurerm_resource_group.rg.location

    security_rule {
        name = "80-in"
        priority = 100
        direction = "Inbound"
        access = "Allow"
        protocol = "Tcp"
        source_port_range = "*"
        destination_port_range = "80"
        source_address_prefix = "*"
        destination_address_prefix = "*"
    }

        security_rule {
        name = "ssh-in"
        priority = 110
        direction = "Inbound"
        access = "Allow"
        protocol = "Tcp"
        source_port_range = "*"
        destination_port_range = "22"
        source_address_prefix = "*"
        destination_address_prefix = "*"
    }
}

# Public IP
resource "azurerm_public_ip" "api" {
    name = "${var.prefix}-api-ip"
    resource_group_name = var.resource_group_name
    location = var.resource_group_location
    allocation_method = "Static"
    sku = "Standard"
}
