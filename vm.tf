
# Network Interface
resource "azurerm_network_interface" "api" {
  name = "${var.prefix}-app-nic"
  resource_group_name = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location

  ip_configuration {
    name = "internal"
    subnet_id = azurerm_subnet.api.id
    private_ip_address_allocation = "Static"
    private_ip_address = "10.60.1.10"
    public_ip_address_id = azurerm_public_ip.api.id
  }
}

resource "azurerm_subnet_network_security_group_association" "api" {
  subnet_id                 = azurerm_subnet.api.id
  network_security_group_id = azurerm_network_security_group.api.id
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "api" {
  name                  = "${var.prefix}-api"
  resource_group_name   = azurerm_resource_group.rg.name
  location              = azurerm_resource_group.rg.location
  size                  = var.vm_size
  admin_username        = "bookmark-admin"
  network_interface_ids = [azurerm_network_interface.api.id]
  custom_data           = local.api_cloud_init

  admin_ssh_key {
    username   = "bookmark-admin"
    public_key = var.admin_ssh_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }
}

# The boot script
locals {
  api_cloud_init = base64encode(templatefile("${path.module}/cloud-init-api.yaml",
  {db_password = var.db_password}
  ))
}

output "public_ip" {
  value = azurerm_public_ip.api.ip_address
}