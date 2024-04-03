# Data Engineering ZoomCamp Project 2024

## Prerequisites

* **Operating System:**  macOS, Linux (Ubuntu, Debian, RedHat) 
* **Software:**
    *  Terraform (version >= 1.4.0) ([https://learn.hashicorp.com/tutorials/terraform/install-cli](https://learn.hashicorp.com/tutorials/terraform/install-cli))
    *  dbt (version >= 1.3.0) ([https://docs.getdbt.com/docs/installation](https://docs.getdbt.com/docs/installation))
    *  Python (version >= 3.8) 
    *  Docker 
    *  Mage  
* **Google Cloud Project:** 
    *  Project with BigQuery and Cloud Storage APIs enabled
    *  Service account with appropriate permissions (BigQuery Data Editor, Storage Object Admin, etc.) 
* **Environment Variables:**
   * `GOOGLE_APPLICATION_CREDENTIALS` (Path to your service account key file)

## Project Structure

* `dezc_project_2024/`
    * [`terraform/`](./infrastructure/) - Contains terraform configuration for provisioning GCP Infrastructure (Cloud Storage, Big Query)