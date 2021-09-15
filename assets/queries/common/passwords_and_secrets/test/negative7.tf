resource "google_container_cluster" "primary3" {
  name               = "marcellus-wallace"
  location           = "us-central1-a"
  initial_node_count = 3

  master_auth {
    username = "1234567890qwertyuiopasdfghjklçzxcvbnm"
    password = ""
    allow_users_to_change_password = true

    client_certificate_config {
      issue_client_certificate = true
    }
  }

  timeouts {
    create = "30m"
    update = "40m"
  }
}
