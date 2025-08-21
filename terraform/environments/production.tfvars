# Environment-specific configuration for production
project_name = "crawler-platform"
environment  = "production"
aws_region   = "us-west-2"

# State management
terraform_state_bucket = "crawler-platform-terraform-state-prod"

# Network Configuration
vpc_cidr = "10.1.0.0/16"
private_subnet_cidrs = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
public_subnet_cidrs  = ["10.1.101.0/24", "10.1.102.0/24", "10.1.103.0/24"]

# EKS Configuration
kubernetes_version = "1.28"
node_instance_type = "t3.large"
worker_instance_type = "c5.2xlarge"

# Production scaling
min_nodes     = 3
max_nodes     = 20
desired_nodes = 6
worker_replicas = 8
scraper_replicas = 4

# Database Configuration (production-ready)
db_instance_class = "db.r6g.2xlarge"
db_allocated_storage = 500
db_max_allocated_storage = 2000
db_name     = "crawler_db"
db_username = "crawler_user"
# db_password should be set via environment variable or AWS Secrets Manager

# Redis Configuration (production cluster)
redis_node_type = "cache.r6g.xlarge"
redis_num_cache_nodes = 3

# Monitoring (enabled for production)
enable_monitoring = true
enable_logging = true

# Security (restrictive for production)
allowed_cidr_blocks = ["10.1.0.0/16"]  # Only internal VPC traffic
enable_private_endpoints = true

# Backup (comprehensive for production)
backup_retention_days = 30
enable_point_in_time_recovery = true

# Autoscaling (enabled for production)
enable_cluster_autoscaler = true
enable_horizontal_pod_autoscaler = true

# Cost optimization (no spot instances for critical production workloads)
enable_spot_instances = false

# Additional tags
additional_tags = {
  Team        = "platform"
  CostCenter  = "operations"
  Purpose     = "production-workload"
  Compliance  = "required"
  Monitoring  = "critical"
}
