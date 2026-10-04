variable "prefix" {
    description = "Student code, acting as name prefix for every resource"
    type = string
}

variable "location" {
    description = "Region of the resources"
    type = string
}

variable "my_ip" {
    type = string
}

variable "admin_ssh_key" {
    type = string
}

variable "subscription_id" {
    type = string
}

variable "vm_size" {
  type    = string
  default = "Standard_B2ats_v2"
}