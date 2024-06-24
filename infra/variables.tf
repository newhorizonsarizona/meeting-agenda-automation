variable "subscription_id" {
  type = string
  default = "eb792c5c-94c2-48d5-b355-c807ecdbe88e"
}

variable "tenant_id" {
  type = string
  default = "9add987e-b316-43b4-8750-4007763832b0"
}

variable "client_id" {
	type = string
	default = "68e11217-f842-4df4-8720-75a08c58f491"
}

variable "client_secret" {
	type = string
}

variable "resource_group_name" {
  type = string
  default = "weeklymeetingagendars"
}

variable "storage_account_name" {
	type = string
	default = "weeklymeetingagendasa"
}

variable "service_plan_name" {
	type = string
	default = "weeklymeetingagendaplan"
}

variable "function_app_name" {
	type = string
	default = "weeklymeetingagenda"
}