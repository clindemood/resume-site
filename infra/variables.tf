variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID used for constructing repository URLs"
  type        = string
}

variable "domain_name" {
  description = "Domain name for Route53 record"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the ACM certificate for HTTPS"
  type        = string
}

variable "session_redis_url" {
  description = "ARN of the secret or SSM parameter containing the Redis URL for session storage"
  type        = string
}

variable "alb_ingress_cidrs" {
  description = "Allowed CIDR blocks for ALB ingress rules"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
