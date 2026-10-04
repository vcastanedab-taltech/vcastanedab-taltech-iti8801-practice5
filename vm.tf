
# IP
resource "azurerm_network_interface" "api" {
  name = "${var.prefix}-app-nic"
  resource_group_name = var.resource_group_name
  location = var.resource_group_location

  ip_configuration {
    name = "internal"
    subnet_id = var.api_subnet_id
    private_ip_address_allocation = "Static"
    private_ip_address = "10.60.1.10"
  }
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "api" {
  name                  = "${var.prefix}-api"
  resource_group_name   = var.resource_group_name
  location              = var.resource_group_location
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
  app_cloud_init = base64encode(templatefile("${path.module}/cloud-init-api.yaml"))
}