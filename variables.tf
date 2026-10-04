variable "prefix" {
    description = "Student code, acting as name prefix for every resource"
    type = string
}

variable "location" {
    description = "Region of the resources"
    type = string
}

variable "resource_group_name" {
    type = string
}

variable "resource_group_location" {
    type = string
}

variable "my_ip" {
    type = string
}