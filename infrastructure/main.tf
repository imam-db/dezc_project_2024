resource "google_storage_bucket" "election_data_bucket" {
  location    = var.location
  name        = var.bucket_name
  project     = var.project_id
}

# Create the BigQuery Dataset
resource "google_bigquery_dataset" "election_results" {
  dataset_id = var.dataset_name
  location   = var.location
  project    = var.project_id # Connect the dataset to the project
}