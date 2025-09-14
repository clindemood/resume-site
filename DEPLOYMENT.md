# Deployment

This project can be hosted on AWS in a few different ways. Below are two common approaches.

## Option A – Single container/EC2

1. Create an ECR repository and push the container image.

   ```bash
   aws ecr create-repository --repository-name resume-site --region <region>

   docker build -t resume-site:latest .
   aws ecr get-login-password --region <region> \
     | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
   docker tag resume-site:latest <account-id>.dkr.ecr.<region>.amazonaws.com/resume-site:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/resume-site:latest
   ```

2. Launch the container on ECS Fargate or an EC2 instance behind an ALB.

   ```bash
   aws ecs run-task --cluster resume-cluster --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-abc],securityGroups=[sg-123],assignPublicIp=ENABLED}" \
     --task-definition resume-site
   ```

3. Configure an Application Load Balancer and target group, then expose port 80/443.

   ```bash
   aws elbv2 create-target-group --name resume-tg --protocol HTTP --port 80 --vpc-id vpc-123
   aws elbv2 register-targets --target-group-arn <tg-arn> --targets Id=<ecs-task-id>
   aws elbv2 create-listener --load-balancer-arn <lb-arn> --protocol HTTP --port 80 \
     --default-actions Type=forward,TargetGroupArn=<tg-arn>
   ```

4. Point your domain to the load balancer using Route53.

   ```bash
   aws route53 change-resource-record-sets --hosted-zone-id <zone-id> --change-batch file://dns.json
   ```

## Deploying to AWS ECS (Fargate)

### Prerequisites

Before deploying you will need:

- An AWS account with permissions to create ECR, ECS, load balancer, Route53 and IAM resources.
- The [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) configured with `aws configure`.
- [Terraform](https://developer.hashicorp.com/terraform/downloads) installed.
- Docker and an ECR repository where the image will be stored.

### Build and push the image

```bash
docker build -t resume-site:latest .
aws ecr get-login-password --region <region> \
  | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag resume-site:latest <account-id>.dkr.ecr.<region>.amazonaws.com/resume-site:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/resume-site:latest
```

### Provision infrastructure with Terraform

The Terraform code under [`infra/`](infra) sets up the ECR repository, ECS cluster
and service, load balancer and DNS records. Run the following from the repo root:

```bash
cd infra
terraform init
terraform apply \
  -var="aws_region=us-east-1" \
  -var="aws_account_id=123456789012" \
  -var="domain_name=example.com" \
  -var="certificate_arn=arn:aws:acm:us-east-1:123456789012:certificate/abc" \
  -var="session_redis_url=arn:aws:ssm:us-east-1:123456789012:parameter/redis_url"
```

Required variables:

- **aws_region** – AWS region for all resources.
- **aws_account_id** – your 12‑digit AWS account number used to form the ECR URL.
- **domain_name** – domain that will point at the load balancer.
- **certificate_arn** – ACM certificate ARN for HTTPS on the load balancer.
- **session_redis_url** – ARN of a secret or SSM parameter containing the Redis connection string for session storage.

When `terraform apply` finishes it will output the ECR repository URL and the
load balancer DNS name. Point your domain to that DNS name if you supplied a
Route53 hosted zone.

### Scaling and rolling out updates

- To scale the service: `aws ecs update-service --cluster resume-cluster --service resume-service --desired-count 2`
- To deploy a new image: rebuild and push the image, then run
  `aws ecs update-service --cluster resume-cluster --service resume-service --force-new-deployment`

### Troubleshooting

- **Access denied**: ensure your IAM user or role has permissions for ECR, ECS and IAM. Re‑run `aws configure` or use a profile with the correct permissions.
- **Image pull errors**: verify `docker push` succeeded and that the ECS task definition uses the correct repository URL and tag. If needed, rerun the ECR login command.
- **Terraform errors**: confirm AWS credentials and required variables are set. Use `-auto-approve` carefully and review the plan output.

### Clean up

Destroy all resources when finished:

```bash
terraform destroy \
  -var="aws_region=us-east-1" \
  -var="aws_account_id=123456789012" \
  -var="domain_name=example.com" \
  -var="certificate_arn=arn:aws:acm:us-east-1:123456789012:certificate/abc" \
  -var="session_redis_url=arn:aws:ssm:us-east-1:123456789012:parameter/redis_url"
```

This removes the ECS service, load balancer, DNS records and ECR repository to
prevent ongoing charges.

## Option B – Static hosting + serverless API

1. Upload files under `app/static/` to an S3 bucket configured for static website hosting or fronted by CloudFront.
2. Package the FastAPI app for AWS Lambda using [Mangum](https://github.com/jordaneremieff/mangum) or a similar ASGI adapter.
3. Deploy the function behind API Gateway with endpoints under `/api/*` and enable CORS for your static site's origin.
4. Update any front-end code if the API lives on a different domain.

## General notes

- Include the JSON data files in your deployment artifact so the API can load resume content.
- No external database is required; sessions are kept in memory.
- Use CloudWatch Logs or similar monitoring to track runtime errors and access logs.
