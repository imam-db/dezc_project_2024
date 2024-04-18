resource "google_storage_bucket" "election_data_bucket" {
  location    = var.location
  name        = var.bucket_name
  project     = var.project_id
}

resource "google_storage_bucket_object" "location_folder" {
  name      = "location/"  # Add trailing slash for consistency
  bucket    = google_storage_bucket.election_data_bucket.name
  content = " "
}

resource "google_storage_bucket_object" "president_folder" {
  name      = "president/"  # Add trailing slash for consistency
  bucket    = google_storage_bucket.election_data_bucket.name
  content = " "
}

resource "google_storage_bucket_object" "dpr_folder" {
  name      = "dpr/"  # Add trailing slash for consistency
  bucket    = google_storage_bucket.election_data_bucket.name
  content = " "
}

# Create the BigQuery Dataset
resource "google_bigquery_dataset" "election_results" {
  dataset_id = var.dataset_name
  location   = var.location
  project    = var.project_id # Connect the dataset to the project
}