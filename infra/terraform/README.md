# Terraform Infrastructure for Scrapy Project

This directory contains Terraform configurations for deploying the scraping infrastructure across different environments.

## Directory Structure

```
terraform/
├── modules/
│   ├── network/        # VPC, subnets, security groups
│   ├── eks/           # Kubernetes cluster
│   ├── rds/           # PostgreSQL database
│   ├── redis/         # Redis cache
│   └── s3/            # S3 buckets for storage
├── envs/
│   ├── dev/           # Development environment
│   ├── staging/       # Staging environment
│   └── prod/          # Production environment
└── README.md          # This file
```

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **Terraform** v1.5.0 or later installed
3. **kubectl** configured for Kubernetes access
4. **Appropriate IAM permissions** for resource creation

## Quick Start

### 1. Initialize Terraform

```bash
cd envs/dev  # or staging/prod
terraform init
```

### 2. Plan Deployment

```bash
terraform plan -var-file="terraform.tfvars"
```

### 3. Apply Configuration

```bash
terraform apply -var-file="terraform.tfvars"
```

### 4. Configure kubectl

```bash
aws eks update-kubeconfig --region eu-west-1 --name scrapy-dev-cluster
```

## Environment Configuration

### Development (`envs/dev/`)

- **Purpose**: Local development and testing
- **Resources**: Minimal, cost-optimized
- **Database**: Single-AZ RDS instance
- **Kubernetes**: 2-node cluster
- **Storage**: Basic S3 buckets

### Staging (`envs/staging/`)

- **Purpose**: Pre-production testing
- **Resources**: Production-like but smaller
- **Database**: Multi-AZ RDS with read replica
- **Kubernetes**: 3-node cluster with autoscaling
- **Storage**: S3 with lifecycle policies

### Production (`envs/prod/`)

- **Purpose**: Live production workloads
- **Resources**: High availability, performance optimized
- **Database**: Multi-AZ RDS with encryption
- **Kubernetes**: Multi-AZ cluster with autoscaling
- **Storage**: S3 with versioning, encryption, lifecycle

## Modules Overview

### Network Module (`modules/network/`)

Creates the foundational networking infrastructure:

- **VPC** with public and private subnets
- **Internet Gateway** and **NAT Gateways**
- **Route tables** and **Security Groups**
- **VPC Endpoints** for AWS services

**Key Features:**
- Multi-AZ deployment for high availability
- Separate subnets for different tiers (public, private, database)
- Security groups with least-privilege access
- VPC Flow Logs for monitoring

### EKS Module (`modules/eks/`)

Provisions a managed Kubernetes cluster:

- **EKS Cluster** with managed node groups
- **IAM roles** and **service accounts**
- **Add-ons**: AWS Load Balancer Controller, EBS CSI Driver
- **Cluster autoscaler** configuration

**Key Features:**
- Multiple node groups for different workload types
- Spot instances for cost optimization (non-production)
- Encryption at rest and in transit
- Network policies for security

### RDS Module (`modules/rds/`)

Sets up PostgreSQL database infrastructure:

- **RDS PostgreSQL** instance or cluster
- **Subnet group** for database placement
- **Parameter group** with optimized settings
- **Security group** for database access

**Key Features:**
- Automated backups with point-in-time recovery
- Read replicas for scaling (staging/production)
- Encryption at rest with KMS
- Enhanced monitoring and performance insights

### Redis Module (`modules/redis/`)

Creates Redis infrastructure for caching and queuing:

- **ElastiCache Redis** cluster
- **Subnet group** for Redis placement
- **Parameter group** with custom settings
- **Security group** for Redis access

**Key Features:**
- Multi-AZ deployment with automatic failover
- Encryption in transit and at rest
- Backup and restore capabilities
- CloudWatch monitoring integration

### S3 Module (`modules/s3/`)

Provisions S3 buckets for data storage:

- **Raw HTML storage** bucket
- **Processed data** bucket
- **Database backups** bucket
- **Application logs** bucket

**Key Features:**
- Lifecycle policies for cost optimization
- Versioning and cross-region replication
- Server-side encryption with KMS
- Access logging and monitoring

## Configuration Variables

### Common Variables

```hcl
# General configuration
project_name    = "scrapy"
environment     = "dev"  # dev, staging, prod
region         = "eu-west-1"
availability_zones = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]

# Networking
vpc_cidr = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
database_subnet_cidrs = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]

# Database
db_instance_class = "db.t3.micro"  # Adjust per environment
db_allocated_storage = 20
db_max_allocated_storage = 100

# Redis
redis_node_type = "cache.t3.micro"  # Adjust per environment
redis_num_cache_nodes = 1

# EKS
eks_node_groups = {
  general = {
    instance_types = ["t3.medium"]
    min_size      = 1
    max_size      = 3
    desired_size  = 2
  }
}
```

### Environment-Specific Overrides

Each environment directory contains:

- `terraform.tfvars` - Environment-specific variable values
- `backend.tf` - Terraform state backend configuration
- `main.tf` - Main configuration importing modules
- `variables.tf` - Variable declarations
- `outputs.tf` - Output values

## State Management

Terraform state is stored in S3 with DynamoDB locking:

```hcl
terraform {
  backend "s3" {
    bucket         = "scrapy-terraform-state-dev"
    key            = "terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "scrapy-terraform-locks"
  }
}
```

## Security Considerations

### IAM Policies

- **Principle of least privilege** applied to all roles
- **Separate roles** for different services and environments
- **Cross-account access** restricted and monitored

### Network Security

- **Private subnets** for application and database tiers
- **Security groups** with minimal required access
- **NACLs** for additional network layer security
- **VPC Flow Logs** enabled for monitoring

### Data Protection

- **Encryption at rest** for all data stores
- **Encryption in transit** for all communications
- **KMS keys** with rotation enabled
- **Backup encryption** with separate keys

## Monitoring and Logging

### CloudWatch Integration

```hcl
# Example CloudWatch configuration
cloudwatch_log_retention_in_days = 30
enable_flow_logs = true
enable_eks_logging = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
```

### Monitoring Stack

- **CloudWatch** for AWS service metrics
- **Prometheus** for application metrics (deployed via Helm)
- **Grafana** for visualization (deployed via Helm)
- **AlertManager** for alerting (deployed via Helm)

## Cost Optimization

### Development Environment

- Use **t3.micro** instances where possible
- **Single-AZ** deployments
- **No read replicas** for databases
- **Lifecycle policies** for quick data cleanup

### Production Environment

- **Reserved instances** for steady-state workloads
- **Spot instances** for batch processing
- **Auto-scaling** based on demand
- **S3 Intelligent Tiering** for storage optimization

## Deployment Workflow

### 1. Local Development

```bash
# Plan changes locally
terraform plan -var-file="terraform.tfvars"

# Apply with approval
terraform apply -var-file="terraform.tfvars"
```

### 2. CI/CD Pipeline

The deployment is automated via GitHub Actions:

1. **Terraform Plan** on pull requests
2. **Terraform Apply** on main branch pushes
3. **State validation** and **drift detection**
4. **Cost estimation** with Infracost

### 3. Environment Promotion

```bash
# Export configuration from staging
terraform output -json > staging-outputs.json

# Import to production planning
terraform plan -var-file="terraform.tfvars" \
  -var="staging_outputs=staging-outputs.json"
```

## Troubleshooting

### Common Issues

1. **State Lock Issues**
   ```bash
   terraform force-unlock <lock-id>
   ```

2. **Resource Conflicts**
   ```bash
   terraform import <resource-type>.<resource-name> <resource-id>
   ```

3. **Permission Errors**
   - Check IAM policies and roles
   - Verify AWS CLI configuration
   - Ensure cross-account permissions if applicable

### Debugging Commands

```bash
# Enable detailed logging
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform.log

# Validate configuration
terraform validate

# Check resource dependencies
terraform graph | dot -Tpng > graph.png
```

## Maintenance

### Regular Tasks

1. **Update Terraform version** and provider versions
2. **Review and update** variable values per environment
3. **Monitor costs** and optimize resource usage
4. **Update security groups** and IAM policies as needed
5. **Test disaster recovery** procedures

### Backup Procedures

- **Terraform state** is automatically backed up to S3
- **Database backups** are handled by RDS automated backups
- **Application data** in S3 has versioning enabled
- **Configuration backups** are stored in Git

## Support and Documentation

- **Internal Wiki**: [Link to internal documentation]
- **Slack Channel**: #infrastructure
- **On-call Rotation**: [Link to PagerDuty]
- **Runbooks**: Located in `/docs/runbooks/`

## Contributing

1. Create feature branch from `main`
2. Make changes in appropriate environment
3. Run `terraform plan` and verify changes
4. Create pull request with plan output
5. After approval, merge triggers automated apply

For more detailed information, see the individual module documentation in their respective directories.
