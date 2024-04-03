variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "dataset_name" {
  description = "The name of the BigQuery dataset"
  type        = string
}

variable "bucket_name" {
  description = "The name of the Cloud Storage bucket"
  type        = string
}

variable "location" {
  description = "The region for the dataset and bucket"
  type        = string
  default     = "US"
}