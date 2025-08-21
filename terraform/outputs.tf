# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

# EKS Outputs
output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.eks.cluster_arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_primary_security_group_id" {
  description = "Cluster security group that was created by Amazon EKS for the cluster"
  value       = module.eks.cluster_primary_security_group_id
}

# Node Group Outputs
output "eks_managed_node_groups" {
  description = "Map of attribute maps for all EKS managed node groups created"
  value       = module.eks.eks_managed_node_groups
}

output "eks_managed_node_groups_autoscaling_group_names" {
  description = "List of the autoscaling group names created by EKS managed node groups"
  value       = module.eks.eks_managed_node_groups_autoscaling_group_names
}

# Database Outputs
output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}

output "db_instance_address" {
  description = "RDS instance hostname"
  value       = aws_db_instance.main.address
  sensitive   = true
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "db_instance_name" {
  description = "RDS instance name"
  value       = aws_db_instance.main.db_name
}

# Redis Outputs
output "redis_replication_group_id" {
  description = "ID of the ElastiCache replication group"
  value       = aws_elasticache_replication_group.main.replication_group_id
}

output "redis_primary_endpoint_address" {
  description = "Address of the endpoint for the primary node in the replication group"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}

output "redis_configuration_endpoint_address" {
  description = "Address of the replication group configuration endpoint when cluster mode is enabled"
  value       = aws_elasticache_replication_group.main.configuration_endpoint_address
  sensitive   = true
}

# ECR Outputs
output "ecr_repository_url_app" {
  description = "URL of the ECR repository for the app"
  value       = aws_ecr_repository.app.repository_url
}

output "ecr_repository_url_worker" {
  description = "URL of the ECR repository for workers"
  value       = aws_ecr_repository.worker.repository_url
}

output "ecr_repository_url_browser" {
  description = "URL of the ECR repository for browser workers"
  value       = aws_ecr_repository.browser.repository_url
}

# IAM Outputs
output "eks_admin_role_arn" {
  description = "ARN of the EKS admin role"
  value       = aws_iam_role.eks_admin.arn
}

output "worker_node_role_arn" {
  description = "ARN of the worker node IAM role"
  value       = module.eks.eks_managed_node_groups["main"].iam_role_arn
}

# ALB Outputs
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = try(kubernetes_service.web.status.0.load_balancer.0.ingress.0.hostname, null)
}

# Security Group Outputs
output "database_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.rds.id
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = aws_security_group.redis.id
}

# Configuration for kubectl
output "configure_kubectl" {
  description = "Configure kubectl: run the following command to update your kubeconfig"
  value = "aws eks --region ${var.aws_region} update-kubeconfig --name ${module.eks.cluster_id}"
}

# Environment Configuration
output "environment_config" {
  description = "Environment configuration for applications"
  value = {
    environment = var.environment
    region      = var.aws_region
    cluster_name = module.eks.cluster_id
    database_url = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}"
    redis_url    = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379"
  }
  sensitive = true
}
