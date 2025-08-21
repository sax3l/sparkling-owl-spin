# Environment-specific configuration for development
project_name = "crawler-platform"
environment  = "development"
aws_region   = "us-west-2"

# State management
terraform_state_bucket = "crawler-platform-terraform-state-dev"

# Network Configuration
vpc_cidr = "10.0.0.0/16"
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

# EKS Configuration
kubernetes_version = "1.28"
node_instance_type = "t3.medium"
worker_instance_type = "t3.large"

# Scaling for development
min_nodes     = 1
max_nodes     = 5
desired_nodes = 2
worker_replicas = 1
scraper_replicas = 1

# Database Configuration (smaller for dev)
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_max_allocated_storage = 100
db_name     = "crawler_db_dev"
db_username = "crawler_dev"
# db_password should be set via environment variable or separate file

# Redis Configuration (smaller for dev)
redis_node_type = "cache.t3.micro"
redis_num_cache_nodes = 1

# Monitoring (disabled for cost saving in dev)
enable_monitoring = false
enable_logging = false

# Security (more permissive for dev)
allowed_cidr_blocks = ["0.0.0.0/0"]
enable_private_endpoints = false

# Backup (shorter retention for dev)
backup_retention_days = 3
enable_point_in_time_recovery = false

# Autoscaling (disabled for predictable costs in dev)
enable_cluster_autoscaler = false
enable_horizontal_pod_autoscaler = false

# Cost optimization
enable_spot_instances = true
spot_instance_types = ["t3.medium", "t3.large"]

# Additional tags
additional_tags = {
  Team        = "development"
  CostCenter  = "engineering"
  Purpose     = "development-testing"
}
