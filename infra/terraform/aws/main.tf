terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "network" {
  source = "./modules/network"

  project_name = var.project_name
}

# Phase 6 will add EKS, ECR, RDS Postgres, ElastiCache Redis, IAM, and observability resources.
# Keep this file plan-safe until the account, region, and budget guardrails are confirmed.

